import os

CONFIG = {
    "database": {
        'NAME': os.getenv('LOCAL_DB_NAME', 'server_template'),
        'HOST': os.getenv('LOCAL_DB_HOST', '0.0.0.0'),
        'USER': os.getenv('LOCAL_DB_USER', 'postgres'),
        'PASS': None,
        'PORT': 5432
    },
    "email": {
        'HOST': os.getenv('EMAIL_HOST'),
        'USER': os.getenv('EMAIL_USER'),
        'PASS': os.getenv('EMAIL_PASS'),
        'PORT': 587
    },
    "local": {
        'ROOT': os.getenv('LOCAL_ROOT'),
        'STORAGE': os.getenv('LOCAL_STORAGE'),
        'SECRET_KEY': os.getenv('SECRET_KEY')
    }
}
