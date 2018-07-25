"""Django settings for stcadmin project."""

import os

from ccapi import CCAPI

from . import local_settings

PROJECT_DIR = local_settings.PROJECT_DIR
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = local_settings.DEBUG
DATABASES = local_settings.DATABASES
ALLOWED_HOSTS = local_settings.ALLOWED_HOSTS
ADMINS = local_settings.ADMINS
EMAIL_HOST = local_settings.EMAIL_HOST
EMAIL_HOST_USER = local_settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = local_settings.EMAIL_HOST_PASSWORD
EMAIL_PORT = local_settings.EMAIL_PORT
EMAIL_USE_TLS = local_settings.EMAIL_USE_TLS
SERVER_EMAIL = local_settings.SERVER_EMAIL
DEFAULT_FROM_EMAIL = local_settings.DEFAULT_FROM_EMAIL
CC_DOMAIN = local_settings.CC_DOMAIN
CC_USERNAME = local_settings.CC_USERNAME
CC_PWD = local_settings.CC_PWD
SPRING_COURIER_RULES = local_settings.SPRING_COURIER_RULES
SCAYT_CUSTOMER_ID = local_settings.SCAYT_CUSTOMER_ID
SpringManifestSettings = local_settings.SpringManifestSettings

# This Security Key must be overriden in production.
SECRET_KEY = '@cy+o@khyz!qttree+#md!1hl#c7w3qf_0^cy-r5%)5f5#2^zt'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'formtools',
    'stcadmin',
    'home',
    'suppliers',
    'labelmaker',
    'reference',
    'user',
    'epos',
    'inventory',
    'list_input',
    'print_audit',
    'spring_manifest',
    'price_calculator',
    'django_markup',
    'stock_check',
    'jchart',
    'profit_loss',
    'product_editor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'stcadmin.urls'

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
                "django.template.context_processors.media",
            ],
        },
    },
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'stcadmin/static'),
]

WSGI_APPLICATION = 'stcadmin.wsgi.application'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'management_commands': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'product_creation': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'file_manifest': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(
    os.path.abspath(os.path.dirname(BASE_DIR)), 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(BASE_DIR)), 'media')

DOCS_ROOT = os.path.join(BASE_DIR, 'docs', 'build', 'html')

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'home:index'

CCAPI.create_session(domain=CC_DOMAIN, username=CC_USERNAME, password=CC_PWD)
