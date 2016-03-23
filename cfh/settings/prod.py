from .base import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

# see description in base.py
SHOW_ONLY_MODERATED = True

# see description in base.py
SYNCHRONIZE_WITH_OPEN_311 = True

OPEN311_API_KEY = os.environ['OPEN311_API_KEY']
