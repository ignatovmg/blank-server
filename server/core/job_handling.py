import json
import logging
import shutil
import subprocess
import os
from copy import deepcopy

from .utils import upload_file, user_tmp_dir
from .models import Job
from .env import SERVER_DIR
from .runner.validate import validate

logger = logging.getLogger('core')


def check_user_input(request):
    """
    Creates a temporary directory in `env.STORAGE`/tmp and creates there user/ where
    the user input is stored. If any error is encountered, removes the directory.

    :param request:
    :return: A tuple of 2 items - list of errors and a path to the temporary directory
    :rtype: (list, path.Path)
    """

    tmp_dir = None
    try:
        error_list = []

        # create a directory to store temporary results
        tmp_dir = user_tmp_dir(request.user.username)
        while tmp_dir.exists():
            tmp_dir = user_tmp_dir(request.user.username)

        tmp_dir.mkdir_p()
        logger.info('Creating %s' % tmp_dir)

        # save user input
        user_dir = tmp_dir.joinpath('user')
        logger.info('Creating directory %s' % user_dir)
        user_dir.mkdir_p()

        logger.info('Saving POST dictionary to %s' % user_dir)
        with open(user_dir.joinpath('user.json'), 'w') as f:
            post_dict = deepcopy(request.POST)
            del post_dict['csrfmiddlewaretoken']
            json.dump(post_dict, f, indent=4)

        logger.info('Saving FILES to %s' % user_dir)
        for name, file in request.FILES.items():
            fpath = user_dir.joinpath(name)
            upload_file(file, fpath)

        # validate and transform raw user input into something
        # more useful (if needed)
        error_list += validate(user_dir)

    except:
        if tmp_dir is not None and tmp_dir.exists():
            tmp_dir.rmtree_p()
        raise

    if error_list:
        if tmp_dir is not None and tmp_dir.exists():
            tmp_dir.rmtree_p()
        return error_list, ''

    return error_list, tmp_dir


def create_job_dir(tmp_dir, job_id):
    """
    Move temporary directory to the permanent storage

    :param `path.Path` tmp_dir: Temporary job directory
    :param int job_id: Job ID
    :return:
    """
    logger.info('Creating job directory ..')
    job = Job.objects.get(job_id=job_id)
    job_dir = job.get_dir()

    if job_dir.isdir():
        shutil.rmtree(job_dir)

    logger.info('Moving %s --> %s' % (tmp_dir, job_dir))
    tmp_dir.move(job_dir)


def submit_job(job_id):  # TODO: see if we can change this
    """
    Run job with the given id

    :param int job_id:
    :return:
    """
    if os.system('ps aux | grep -v grep | grep -o "job_id=%i"' % job_id) == 0:
        logger.warning('Job %i is still running!' % job_id)
        return ['Job %i is still running!' % job_id] 

    job = Job.objects.get(job_id=job_id)
    job.reset()
    cmd = 'from core.runner.runner import run_job; from core.models import Job; run_job(Job.objects.get(job_id=%i))' % job_id
    exe = SERVER_DIR.joinpath('manage.py').abspath()
    with open(job.get_dir().joinpath('stdout.log'), 'a') as o, open(job.get_dir().joinpath('stderr.log'), 'a') as e:
        subprocess.Popen(['python', exe, 'shell', '-c', '%s' % cmd], stdout=o, stderr=e)
    
    return []
