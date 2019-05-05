from django.db import models
from django.contrib.auth.models import User
from . import env

import json


class Job(models.Model):
    STATUS_CHOICES = (
        ('L.STR', 'Started the job'),
        ('L.PRE', 'Doing something'),
        ('L.CPL', 'Job completed'),
        ('L.ERR', 'Error'),
        ('R.ERR', 'Error'),
    )

    job_id = models.AutoField(primary_key=True)
    job_name = models.CharField(max_length=30, default="")
    created = models.DateTimeField(auto_now_add=True)
    warning = models.CharField(max_length=1000, default="", blank=True)
    error = models.CharField(max_length=1000, default="", blank=True)
    deleted = models.BooleanField(default=False)
    restarted = models.IntegerField(default=0)
    touched = models.DateTimeField(auto_now=True)
    queue_id = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()

    status = models.CharField(max_length=5, choices=STATUS_CHOICES)
    details_json = models.CharField(max_length=1000, blank=True)

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

    def reset(self):
        """
        Call this when a job is (re)started. Resets error and warning and increments 'restarted' field
        :return: None
        """
        self.restarted += 1
        self.error = ''
        self.warning = ''
        self.save()

    def get_dir(self):
        """
        Get path to job directory
        :return: Job directory
        :rtype: Path
        """
        return env.JOBS_DIR.joinpath(str(self.job_id))

    def get_output_dir(self):
        """
        Get path to the directory, where job output is stored
        :return: Output directory
        :rtype: Path
        """
        return self.get_dir().joinpath('output')

    def get_user_dir(self):
        """
        Get path to user directory of the job
        :return: User directory
        :rtype: Path
        """
        return self.get_dir().joinpath('user')

    def get_user_json(self):
        """
        Get path of the json file with job parameters
        :return: Json file
        :rtype: Path
        """
        return self.get_user_dir().joinpath('user.json')
