"""
All the environmental variables are kept here and
are passed to all templates through add_env_vars(),
which is specified in server/settings.py as an
additional context processor
"""

from path import Path
from server.config import CONFIG

SERVER_NAME = "TEMPLATE"

# some paths
ENV_PATH = Path(__file__).abspath()
SERVER_DIR = Path(CONFIG['local']['ROOT'])
STORAGE_DIR = Path(CONFIG['local']['STORAGE'])
JOBS_DIR = STORAGE_DIR.joinpath('jobs')
TMP_DIR = STORAGE_DIR.joinpath('tmp')
CORE_DIR = SERVER_DIR.joinpath('core')
JOBS_PER_PAGE = 10

# universal template context (added to all templates)
env = {
    'SERVER_NAME': SERVER_NAME,
}


def add_env_vars(request):
    return env
