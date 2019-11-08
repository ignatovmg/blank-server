from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import File

import json
import logging
import tempfile
from time import sleep
from path import Path
from celery import shared_task

from . import env
from .utils import upload_file


def _get_task_logger(job_id):
    logger = logging.getLogger(str(job_id))
    logger.setLevel(logging.DEBUG)
    job = Job.objects.get(job_id=job_id)
    h = logging.FileHandler(job.get_dir().joinpath('log.txt'), mode='a')
    f = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    h.setFormatter(f)
    logger.addHandler(h)
    return logger

# TODO: turn off celery logging. Celery keeps dumping everything to the logfile, which can become really large
@shared_task(bind=True, acks_late=True, track_started=True, default_retry_delay=30, autoretry_for=(Exception,), max_retries=1)
def submit_job(self, job_id):
    logger = _get_task_logger(job_id)
    try:
        job = Job.objects.get(job_id=job_id)
        cur_status = job.status
        if cur_status in Job.STATUS_FINISHED:
            logger.info(f'Starting job {job_id} in L.STR (currently in {cur_status})')
            job.status = 'L.STR'
            job.save()
        else:
            logger.info(f'Starting job {job_id} in {cur_status} (it was interrupted half-way)')

        if job.status == 'L.STR':
            logger.info(f'Started {job.status}')
            sleep(10)
            job.status = 'L.RUN'
            job.save()

        if job.status == 'L.RUN':
            logger.info(f'Running {job.status}')
            sleep(10)

            result = job.summant1 + job.summant2
            outdir = job.get_output_dir()
            outdir.mkdir_p()
            job.get_result_file().write_text(str(result) + '\n')

            job.status = 'L.FIN'
            job.save()

        if job.status == 'L.FIN':
            logger.info(f'Finalizing {job.status}')
            sleep(10)
            job.status = 'L.CPL'
            job.save()

        if job.status == 'L.CPL':
            logger.info(f'Finished {job.status}')

    except Exception as e:
        logger.exception(e)
        Job.objects.get(job_id=job_id).local_error('Unknown error')
        raise

    return None


class Job(models.Model):
    STATUS_CHOICES = (
        ('L.STR', 'Starting the job'),
        ('L.RUN', 'Running'),
        ('L.FIN', 'Running'),
        ('L.CPL', 'Job completed'),
        ('L.ERR', 'Error'),
    )

    # All other statuses mean the job is still running
    STATUS_FINISHED = ('L.CPL', 'L.ERR')

    job_id = models.AutoField(primary_key=True)
    job_name = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    warning = models.CharField(max_length=1000, blank=True)
    error = models.CharField(max_length=1000, blank=True)
    deleted = models.BooleanField(default=False)
    restarted = models.IntegerField(default=0)
    touched = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    celery_id = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='L.STR')
    details_json = models.CharField(max_length=1000, blank=True)

    _temp_dir = ''

    def __str__(self):
        attr_list = [self.job_id, self.user, self.status]
        return '-'.join(map(str, attr_list))

    def __getattr__(self, attr):
        json_str = super(Job, self).__getattribute__("details_json")
        if json_str:
            json_dict = json.loads(json_str)
            if attr in json_dict:
                return json_dict[attr]
        return super(Job, self).__getattribute__(attr)

    def get_dir(self):
        return env.JOBS_DIR.joinpath(str(self.job_id))

    def get_output_dir(self):
        return self.get_dir().joinpath('output')

    def get_user_dir(self):
        return self.get_dir().joinpath('user')

    def get_user_json(self):
        return self.get_user_dir().joinpath('user.json')

    def get_log_file(self):
        return self.get_dir().joinpath('log.txt')

    def get_result_file(self):
        return self.get_output_dir().joinpath('result.txt')

    def get_result(self):
        with open(self.get_result_file(), 'r') as f:
            r = f.read().strip()
        return r

    def local_error(self, error):
        self.status = 'L.ERR'
        self.error = error
        self.save()

    def reset(self):
        """
        Call this when a job is (re)started. Resets error and warning and increments 'restarted' field
        """
        self.restarted += 1
        self.error = ''
        self.warning = ''
        self.save()

    def start(self):
        if self.celery_id != '':
            result = submit_job.AsyncResult(self.celery_id)
            if not result.ready():
                return [f'Job {self.job_id} is already running (state: {result.state})']
        result = submit_job.apply_async((self.job_id,))
        self.celery_id = result.task_id
        self.restarted += 1
        self.error = ''
        self.warning = ''
        self.save()
        return []

    def cancel(self):
        if self.celery_id != '':
            result = submit_job.AsyncResult(self.celery_id)
            if result.ready():
                return [f'Job has already finished (state: {result.state})']

            result.revoke(terminate=True)
            return [f'Job cancelled (state: {result.state})']
        else:
            return ['Task id is empty']

    def _make_temp_dir(self):
        self._temp_dir = Path(tempfile.mkdtemp(dir=env.TMP_DIR))
        self._temp_dir.chmod(0o755)

    def _create_job_dir(self):
        job_dir = self.get_dir()
        if job_dir.isdir():
            job_dir.rmtree(job_dir)
        self._temp_dir.move(job_dir)

    def check_user_input(self, form, files):
        error_list = []
        self._make_temp_dir()

        user_dir = self._temp_dir.joinpath('user')
        user_dir.mkdir_p()

        # dump user files in user/
        for name, file in files.items():
            fpath = user_dir.joinpath(file.name)
            upload_file(file, fpath)

        # dump user data in user/user.json
        with open(user_dir.joinpath('user.json'), 'w') as f:
            data = {k: (v if not isinstance(v, File) else v.name) for k, v in form.cleaned_data.items()}
            json.dump(data, f, indent=4)

        return error_list

    def make_dir_and_start(self):
        self._create_job_dir()

        clean_json = self.get_user_json()
        with open(clean_json, 'r') as f:
            details_json = json.load(f)
        self.details_json = json.dumps(details_json)
        self.save()

        self.start()
