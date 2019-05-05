from path import Path
from server.config import CONFIG

ROOT = Path(__file__).abspath().dirname()
REMOTE_BIN = Path(CONFIG['remote']['BIN'])
REMOTE_JOBS = Path(CONFIG['remote']['STORAGE'])
REMOTE_HOST = CONFIG['remote']['HOST']
REMOTE_USER = CONFIG['remote']['USER']
REMOTE_PASSWORD = CONFIG['remote']['PASS']
