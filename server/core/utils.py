import random
import string
import logging
import json
from zipfile import ZipFile
from path import Path

logger = logging.getLogger('core')


def random_string(length=16):
    """
    Make a random string of given length
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join([random.choice(alphabet) for n in range(length)])


def random_string_alphanum(length=16):
    """
    Make a random string of given length
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join([random.choice(alphabet) for n in range(length)])


def upload_file(f, name):
    """
    Upload file obtained from request.FILES
    """
    with open(name, 'wb') as o:
        for chunk in f.chunks():
            o.write(chunk)


def load_json_file(path):
    """
    Get content of a json file. Skips exceptions.
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


def zip_files(f, files, name_list=None):
    if name_list is None:
        name_list = [f.basename() for f in files]

    with ZipFile(f, mode='w') as z:
        for name, file in zip(name_list, files):
            with open(file, 'r') as i:
                z.writestr(name, i.read())
