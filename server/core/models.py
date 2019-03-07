from django.db import models
from django.contrib.auth.models import User

from . import env


class Job(models.Model):
    STATUS_CHOICES = (
        ('L.STR', 'Started on local machine'),
        ('L.ERR', 'Error on local machine'),
        ('L.PRE', 'Preparing data on local machine'),
        ('L.CPY', 'Copying from local to remote machine'),
        ('R.QUE', 'Job queued on remote machine'),
        ('R.ERR', 'Error on remote machine'),
        ('R.RUN', 'Running on remote machine'),
        ('R.CPY', 'Copying from remote to local machine'),
        ('L.FIN', 'Finishing on local machine'),
        ('L.CPL', 'Job completed')
    )

    job_id = models.AutoField(primary_key=True)
    job_name = models.CharField(max_length=30, default="")
    created = models.DateTimeField(auto_now_add=True)
    warning = models.CharField(max_length=100, default="")
    error = models.CharField(max_length=1000, default="")
    deleted = models.BooleanField(default=False)
    restarted = models.IntegerField(default=0)
    touched = models.DateTimeField(auto_now=True)
    queue_id = models.IntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    status = models.CharField(max_length=5, choices=STATUS_CHOICES)

    def __str__(self):
        attr_list = [self.job_id, self.user, self.status]
        return '-'.join(map(str, attr_list))

    def save(self, *args, **kwargs):
        if self.job_name == "":
            self.job_name = str(self.job_id)

        super().save(*args, **kwargs)

    def get_dir(self):
        return env.JOBS_DIR.joinpath(str(self.job_id))

    def set_error(self, error_string):
        self.error = error_string
        self.save()

    def reset(self):
        """
        Call this when a job is (re)started
        :return:
        """
        self.restarted += 1
        self.error = ''
        self.warning = ''
        self.save()

