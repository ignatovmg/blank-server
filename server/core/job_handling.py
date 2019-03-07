import json
import logging
from copy import deepcopy

from .utils import upload_file, user_tmp_dir, clean_dir
from .models import Job

from runner.validate import validate
from runner.runner import run

logger = logging.getLogger(__name__)


def check_job_input(request):
    """
    Creates a temporary directory in STORAGE/tmp and creates there user/ where
    raw user input is stored. If any error is encountered, cleans the directory.

    :rtype: tuple(list, path.Path)
    :param request:
    :return: A tuple of 2 items - list of errors and a path to the temporary directory
    """

    tmp_dir = None
    user_dir = None
    user_fixed_dir = None

    try:
        error_list = []

        ########################################
        # create directory to store temporary results
        tmp_dir = user_tmp_dir(request.user.username)
        while tmp_dir.exists():
            tmp_dir = user_tmp_dir(request.user.username)

        tmp_dir.mkdir_p()
        logger.info('Creating %s' % tmp_dir)

        ########################################
        # save raw user input
        user_dir = tmp_dir.joinpath('user')
        logger.info('Creating directory %s' % user_dir)
        user_dir.mkdir_p()

        logger.info('Saving POST dictionary to %s' % user_dir)
        with open(user_dir.joinpath('user.post'), 'w') as f:
            post_dict = deepcopy(request.POST)
            del post_dict['csrfmiddlewaretoken']
            json.dump(post_dict, f)

        logger.info('Saving FILES to %s' % user_dir)
        for name, file in request.FILES.items():
            fpath = user_dir.joinpath(name)
            upload_file(file, fpath)

        ########################################
        # validate and transform raw user input into something
        # more useful (if needed)
        user_fixed_dir = tmp_dir.joinpath('user_fixed')
        user_fixed_dir.mkdir_p()
        error_list += validate(user_dir, user_fixed_dir)

    except:
        clean_dir(user_dir)
        clean_dir(user_fixed_dir)
        clean_dir(tmp_dir)
        raise

    if error_list:
        clean_dir(user_dir)
        clean_dir(user_fixed_dir)
        clean_dir(tmp_dir)
        return error_list, ''

    return error_list, tmp_dir


def create_job_dir(tmp_dir, job_id):
    """
    Move temporary directory to a permanent storage

    :param tmp_dir: Temporary job directory
    :param job_id: Job ID
    :return:
    """
    job = Job.objects.get(job_id=job_id)
    job_dir = job.get_dir()

    logger.info('Moving %s --> %s' % (job_dir, tmp_dir))
    tmp_dir.move(job_dir)


def submit_job(job):
    run(job)

