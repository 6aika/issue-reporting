from .base import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

# see description in base.py
SHOW_ONLY_MODERATED = True

# see description in base.py
SYNCHRONIZE_WITH_OPEN_311 = True

OPEN311_API_KEY = os.environ['OPEN311_API_KEY']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level': 'INFO',
            'class': 'logging.NullHandler',
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "/var/log/cfh/cfh.log",
            'maxBytes': 50000,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'propagate': True,
            'level': 'INFO',
        },
        'api': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
        },
        'frontend': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
        },
    }
}