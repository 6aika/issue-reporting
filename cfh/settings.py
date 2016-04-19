import os

from environ import Env

env = Env()
DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env.str('SECRET_KEY', default=('cfh' if DEBUG else Env.NOTSET))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'formtools',
    'rest_framework',
    'api',
    'frontend',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cfh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework_xml.parsers.XMLParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'api.renderers.SmartXMLRenderer',
    ),
    'EXCEPTION_HANDLER': 'api.api_utils.api_exception_handler'
}

WSGI_APPLICATION = 'cfh.wsgi.application'

DATABASES = {
    'default': env.db_url(default='postgis://postgres:cfh@localhost:5432/cfh')
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Helsinki'

USE_I18N = True

# Use our own DATETIME format, see below
USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles/")
MEDIA_URL = "/media/"

# Default formatting
DATETIME_FORMAT = "j.n.Y - G:i"
DATE_FORMAT = "j.n.Y"

ALLOW_HELSINKI_SPECIFIC_FEATURES = True

# limit amount of feedback list items if date filters are not provided
FEEDBACK_LIST_LIMIT = 200

# OPEN311 synchronization options
OPEN311_URL = "https://asiointi.hel.fi/palautews/rest/v1"
OPEN311_SERVICE_URL = "https://asiointi.hel.fi/palautews/rest/v1/services.json?locale={}"
SYNCHRONIZATION_START_DATETIME = '2014-09-07T00:00:00'
OPEN311_FEEDBACKS_PER_RESPONSE_LIMIT = 500
OPEN311_RANGE_LIMIT_DAYS = 90
OPEN311_API_KEY = env.str('OPEN311_API_KEY', default='f1301b1ded935eabc5faa6a2ce975f6')

# synchronize all new feedbacks with Open311 immediately
# if false the service_request_id will be generated by city-feedback-hub and
# the pictures will be stored in local database
SYNCHRONIZE_WITH_OPEN_311 = env.bool('SYNCHRONIZE_WITH_OPEN_311', default=False)

# email notifications settings
SEND_STATUS_UPDATE_NOTIFICATIONS = os.environ.get('SEND_STATUS_UPDATE_NOTIFICATIONS', False)
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)
FEEDBACK_DETAILS_URL = os.environ.get('FEEDBACK_DETAILS_URL', 'http://localhost:8000/feedbacks/{}')

EMAIL_SUBJECT = 'City Feedback Hub - Request Status Update'
EMAIL_TEXT = '''Hei! <br><br>
Helsingin kaupungin City Feedback Hub - palautejärjestelmään antamasi palautteen tila on muuttunut. Voit nähdä palautteen ja tarkastella muutoksia klikkaamalla alla olevaa linkkiä.
<br><br>
{{ feedback URL }}
<br><br>
Ystävällisin terveisin,
City Feedback Hub
<br><br>
Huom! Älä vastaa tähän viestiin, sillä vastausviestejä ei käsitellä.'''

# geocoding options
USE_NOMINATIM = False
REVERSE_GEO_URL = 'http://api.hel.fi/servicemap/v1/address/?lat={}&lon={}&page=1'

# option is used to hide feedbacks with status "moderation"
SHOW_ONLY_MODERATED = env.bool("SHOW_ONLY_MODERATED", default=(not DEBUG))

# Set CFH environment variable to apply the path
if "CFH" in os.environ:
    GEOS_LIBRARY_PATH = "/Applications/Postgres.app/Contents/Versions/latest/lib/libgeos_c.dylib"

log_handlers = {
    'null': {'level': 'INFO', 'class': 'logging.NullHandler',},
    'console': {'level': 'INFO', 'class': 'logging.StreamHandler', 'formatter': 'standard'},
}

if env.str("CFH_LOG_FILE", default=None):
    log_handlers["logfile"] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': env.str("CFH_LOG_FILE"),
        'maxBytes': 50000,
        'backupCount': 5,
        'formatter': 'standard',
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': log_handlers,
    'loggers': {
        'django': {
            'handlers': log_handlers.keys(),
            'propagate': True,
            'level': 'WARN',
        },
        'api': {
            'handlers': log_handlers.keys(),
            'level': 'DEBUG',
        },
        'frontend': {
            'handlers': log_handlers.keys(),
            'level': 'DEBUG',
        },
    }
}
