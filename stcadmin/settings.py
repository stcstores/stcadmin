"""Django settings for stcadmin project."""

import os
import sys

import toml
from ccapi import CCAPI
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db import models

models.FieldDoesNotExist = FieldDoesNotExist  # Compatibility for django-polymorphic

CI_ENVIRONMENT = "CI" in os.environ

SOURCE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
BASE_DIR = os.path.dirname(SOURCE_DIR)
CONFIG_DIR = os.path.join(BASE_DIR, "config")

CONFIG_PATH = os.path.join(CONFIG_DIR, "config.toml")

try:
    with open(CONFIG_PATH, "r") as config_file:
        CONFIG = toml.load(config_file)
except Exception:
    raise ImproperlyConfigured("Config file not found.")


def get_config(key):
    """Return the associated value for key from the config file."""
    value = CONFIG.get(key)
    if value is None:
        raise ImproperlyConfigured(f"Config value '{key}' is not set.")
    else:
        return value


# Secret Key
try:
    secret_key_path = os.path.join(CONFIG_DIR, "secret_key.toml")
    with open(secret_key_path, "r") as secret_key_file:
        SECRET_KEY = toml.load(secret_key_file)["SECRET_KEY"]
except Exception:
    raise ImproperlyConfigured("A secret key must be set in stcadmin/secret_key.toml")


DEBUG = get_config("DEBUG")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": get_config("DATABASE_HOST"),
        "NAME": get_config("DATABASE_NAME"),
        "USER": get_config("DATABASE_USER"),
        "PASSWORD": get_config("DATABASE_PASSWORD"),
        "PORT": get_config("DATABASE_PORT"),
        "TEST": {"NAME": get_config("TEST_DATABASE_NAME")},
    }
}
ALLOWED_HOSTS = get_config("ALLOWED_HOSTS")
ADMINS = get_config("ADMINS")
EMAIL_HOST = get_config("EMAIL_HOST")
EMAIL_HOST_USER = get_config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = get_config("EMAIL_PORT")
EMAIL_USE_TLS = get_config("EMAIL_USE_TLS")
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CC_DOMAIN = get_config("CC_DOMAIN_SECRET")
CC_USERNAME = get_config("CC_USERNAME_SECRET")
CC_PWD = get_config("CC_PASS")
SCAYT_CUSTOMER_ID = get_config("SCAYT_CUSTOMER_ID_TOKEN")
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "polymorphic",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "adminsortable2",
    "easy_thumbnails",
    "file_exchange",
    "mathfilters",
    "solo",
    "validation",
    "formtools",
    "stcadmin",
    "home",
    "labelmaker",
    "reference",
    "user",
    "inventory",
    "list_input",
    "price_calculator",
    "django_markup",
    "stock_check",
    "jchart",
    "product_editor",
    "epos",
    "orders",
    "shipping",
    "feedback",
    "fba",
    "channels",
    "purchases",
    "hardware",
    "debug_toolbar",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "stcadmin.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
            ]
        },
    }
]

STATICFILES_DIRS = [os.path.join(SOURCE_DIR, "stcadmin", "static")]

WSGI_APPLICATION = "stcadmin.wsgi.application"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


def add_user_to_log_record(record):
    """Add the user that originated a logging record if possible."""
    if not hasattr(record, "user"):
        try:
            record.user = record.request.user.username
        except AttributeError:
            record.user = None
    return True


def replace_newlines(record):
    """Format log with escaped newlines."""
    record.msg = record.msg.strip().replace("\n", "\\n")
    return True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "add_user_to_log_record": {
            "()": "django.utils.log.CallbackFilter",
            "callback": add_user_to_log_record,
        },
        "replace_newlines": {
            "()": "django.utils.log.CallbackFilter",
            "callback": replace_newlines,
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["add_user_to_log_record"],
            "formatter": "default_formatter",
            "include_html": False,
        },
        "ccapi_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "ccapi.log"),
            "maxBytes": 1_048_576,
            "backupCount": 2,
            "filters": ["add_user_to_log_record", "replace_newlines"],
            "formatter": "default_formatter",
        },
        "order_profit_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "order_profit.log"),
            "maxBytes": 1_048_576,
            "backupCount": 2,
            "formatter": "default_formatter",
            "delay": True,
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "stcadmin_error.log"),
            "maxBytes": 1_048_576,
            "backupCount": 2,
            "level": "ERROR",
            "filters": ["add_user_to_log_record"],
            "formatter": "default_formatter",
        },
        "profit_loss_error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "profit_loss_error.log"),
            "maxBytes": 1_048_576,
            "backupCount": 2,
            "level": "ERROR",
            "filters": ["add_user_to_log_record"],
            "formatter": "default_formatter",
        },
        "product_editor_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "product_editor.log"),
            "maxBytes": 1_048_576,
            "backupCount": 2,
            "filters": ["add_user_to_log_record", "replace_newlines"],
            "formatter": "default_formatter",
        },
        "stdout": {"class": "logging.StreamHandler", "level": "INFO"},
    },
    "loggers": {
        "django": {
            "handlers": ["stdout", "error_file_handler", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        "management_commands": {
            "handlers": ["error_file_handler", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "product_creation": {
            "handlers": ["error_file_handler", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "ccapi.requests.ccapisession": {
            "handlers": ["stdout", "ccapi_file_handler"],
            "level": "DEBUG",
            "propagate": False,
        },
        "ccapi_errors": {
            "handlers": ["mail_admins", "error_file_handler"],
            "level": "ERROR",
            "propagate": False,
        },
        "product_editor": {
            "handlers": ["stdout", "product_editor_file_handler"],
            "level": "DEBUG",
            "propogate": False,
        },
        "order_profit": {
            "handlers": ["profit_loss_error_file_handler"],
            "level": "ERROR",
            "propagate": False,
        },
    },
    "formatters": {
        "default_formatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "user_formatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - User: %(user)s - %(message)s"
        },
    },
}

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DOCS_ROOT = os.path.join(SOURCE_DIR, "docs", "build", "html")

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "home:index"

CELERY_BROKER_URL = get_config("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"


TESTING = (
    len(sys.argv) > 1
    and sys.argv[1] == "test"
    or os.path.basename(sys.argv[0]) in ("pytest", "py.test")
)


def create_CCAPI_session():
    """Create the Cloud Commerce session."""
    if not TESTING and not CI_ENVIRONMENT:
        CCAPI.create_session(domain=CC_DOMAIN, username=CC_USERNAME, password=CC_PWD)
        print("Created Cloud Commerce session.", file=sys.stderr)
    else:
        print("Skipping Cloud Commerce session for testing.", file=sys.stderr)


create_CCAPI_session()
