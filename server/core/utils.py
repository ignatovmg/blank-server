import random
import string
import logging
import json
from path import Path

from . import env

logger = logging.getLogger('core')


def random_string(length=16):
    """
    Make a random string of given length

    :param int length: String length
    :return: Random string
    :rtype: str
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join([random.choice(alphabet) for n in range(length)])


def random_string_alphanum(length=16):
    """
    Make a random string of given length

    :param int length: String length
    :return: Random string
    :rtype: str
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join([random.choice(alphabet) for n in range(length)])


def user_tmp_dir(username):
    """
    Make a random name for a temporary directory in env.TMP_DIR

    :param `django.contrib.auth.models.User` username: Username to prepend the directory name with
    :return: Directory name
    """
    return env.TMP_DIR.joinpath(username + '_' + random_string_alphanum())


def upload_file(f, name):
    """
    Upload file obtained from request.FILES

    :param f: File open for reading
    :param str name: Valid path for upload
    """
    with open(name, 'wb') as o:
        for chunk in f.chunks():
            o.write(chunk)


def load_json_file(path):
    """
    Get content of a json file. Skips exceptions.

    :param str path: Path to json file
    :return: Content of a json file
    :rtype: str
    """
    path = Path(path)
    output = {}
    try:
        with open(path, 'r') as f:
            output = json.load(f)
    except Exception as e:
        logger.exception(e)
        pass
    return output

