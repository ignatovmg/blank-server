import random
import string
import logging

from . import env

logger = logging.getLogger(__name__)


def random_string(length=16):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])


def user_tmp_dir(username):
    return env.TMP_DIR.joinpath(username + '_' + random_string())


def upload_file(f, name):
    with open(name, 'wb') as o:
        for chunk in f.chunks():
            o.write(chunk)


def clean_dir(dir_name):
    if dir_name:
        if dir_name.exists():
            logger.info('Removing %s' % dir_name)
            for f in dir_name.listdir():
                f.remove()
                dir_name.removedirs_p()

