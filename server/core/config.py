from configobj import ConfigObj
from path import Path


DEFAULTS = {
    "database": {
        'NAME': 'postgres',
        'HOST': '127.0.0.1',
        'USER': 'postgres',
        'PASSWORD': None,
    },
    "email": {
        'HOST': 'smtp.gmail.com',
        'USER': None,
        'PASSWORD': None,
        'PORT': 587
    },
    "remote": {
        'HOST': 'scc1.bu.edu',
        'USER': None,
        'PASSWORD': None
    }
}


def get_config(config_path="~/.template_server_rc"):
    config = ConfigObj(DEFAULTS)

    config_file = Path(config_path).expand()
    config.filename = config_file

    if config_file.exists():
        config.merge(ConfigObj(config_file))
    else:
        config.write()

    return config
