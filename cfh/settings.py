import os

import babel
from environ import Env

env = Env()
DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env.str('SECRET_KEY', default=('cfh' if DEBUG else Env.NOTSET))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': env.db_url(default='postgis://postgres:cfh@localhost:5432/cfh')
}

INSTALLED_APPS = list(filter(None, [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'rest_framework',
    'parler',
    'cfh',
    'issues',
    'issues_citysdk',
    'issues_media',
    'issues_hel',
    'issues_log',
    'issues_simple_ui',
    ('issues_geometry' if ('gis' in DATABASES['default']['ENGINE']) else None)
]))

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
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'issues.api.renderers.XMLRenderer',
        'issues.api.renderers.SparkJSONRenderer',
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'issues.api.pagination.GeoReportV2Pagination',
    'PAGE_SIZE': 100,
    'MAX_PAGE_SIZE': 500,
    'EXCEPTION_HANDLER': 'issues.api.utils.api_exception_handler'
}

language_names = babel.Locale('en').languages
LANGUAGES = [
    (code, language_names.get(code, code.title()))
    for code
    in env.str('LANGUAGES', default='en,fi').split(',')
]
LANGUAGE_CODE = LANGUAGES[0][0]
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
MEDIA_URL = '/media/'
ROOT_URLCONF = 'cfh.urls'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
TIME_ZONE = 'Europe/Helsinki'
USE_I18N = True
USE_L10N = True
USE_TZ = True
WSGI_APPLICATION = 'cfh.wsgi.application'
GEOREPORT_API_ROOT = env.str('ISSUES_GEOREPORT_API_ROOT', default='api/georeport/v2/')
ISSUES_DEFAULT_MODERATION_STATUS = env.str('ISSUES_DEFAULT_MODERATION_STATUS', default='public')
ISSUES_GEOMETRY_SRID = env.int('ISSUES_GEOMETRY_SRID', default=4326)
LOGIN_REDIRECT_URL = '/'

PARLER_LANGUAGES = {
    None: [
        {'code': code} for (code, name) in LANGUAGES
    ],
    'default': {
        'fallback': LANGUAGE_CODE,
        'hide_untranslated': False,
    }
}
