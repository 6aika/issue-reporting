from .base import *

DEBUG = True

SECRET_KEY = '^u+g@a2=7bf24$%v5@drqa8s+x4@k!-gmqf@fwnx3a%o^u)akl'

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
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'api': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'frontend': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}