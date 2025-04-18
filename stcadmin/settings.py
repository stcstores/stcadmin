"""Django settings for stcadmin project."""

import os
import sys
import tempfile
from pathlib import Path
from tempfile import SpooledTemporaryFile

import toml
from amapi.session import AmapiSessionUK, AmapiSessionUS
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db import models
from imagekit.cachefiles.backends import AbstractCacheFileBackend
from linnapi import LinnworksAPISession
from shopify_api_py import ShopifyAPISession
from storages.backends.s3boto3 import S3Boto3Storage

models.FieldDoesNotExist = FieldDoesNotExist  # Compatibility for django-polymorphic

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

CI_ENVIRONMENT = "CI" in os.environ

SOURCE_DIR = Path(__file__).parent.parent.absolute()
BASE_DIR = SOURCE_DIR.parent
CONFIG_DIR = BASE_DIR / "config"

CONFIG_PATH = CONFIG_DIR / "config.toml"

try:
    with open(CONFIG_PATH, "r") as config_file:
        CONFIG = toml.load(config_file)
except Exception:
    raise ImproperlyConfigured("Config file not found.") from None


def get_config(key):
    """Return the associated value for key from the config file."""
    value = CONFIG.get(key)
    if value is None:
        raise ImproperlyConfigured(f"Config value {key!r} is not set.")
    else:
        return value


# Secret Key
try:
    secret_key_path = CONFIG_DIR / "secret_key.toml"
    with open(secret_key_path, "r") as secret_key_file:
        SECRET_KEY = toml.load(secret_key_file)["SECRET_KEY"]
except Exception:
    raise ImproperlyConfigured(
        "A secret key must be set in stcadmin/secret_key.toml"
    ) from None


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
        "TIME_ZONE": TIME_ZONE,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "localhost",
    },
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost/",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

SELECT2_CACHE_BACKEND = "select2"

ALLOWED_HOSTS = get_config("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = get_config("CSRF_TRUSTED_ORIGINS")
ADMINS = get_config("ADMINS")
EMAIL_HOST = get_config("EMAIL_HOST")
EMAIL_HOST_USER = get_config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = get_config("EMAIL_PORT")
EMAIL_USE_TLS = get_config("EMAIL_USE_TLS")
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

BUCKET_DOMAIN = get_config("BUCKET_DOMAIN")
BUCKET_ACCESS_KEY = get_config("BUCKET_ACCESS_KEY")
BUCKET_SECRET_KEY = get_config("BUCKET_SECRET_KEY")

SHOPIFY_SHOP_URL = get_config("SHOPIFY_SHOP_URL")
SHOPIFY_API_VERSION = get_config("SHOPIFY_API_VERSION")
SHOPIFY_API_PASSWORD = get_config("SHOPIFY_API_PASSWORD")

LINNAPI_APPLICATION_ID = get_config("LINNAPI_APPLICATION_ID")
LINNAPI_APPLICATION_SECRET = get_config("LINNAPI_APPLICATION_SECRET")
LINNAPI_APPLICATION_TOKEN = get_config("LINNAPI_APPLICATION_TOKEN")

AMAZON_UK_REFRESH_TOKEN = get_config("AMAZON_UK_REFRESH_TOKEN")
AMAZON_UK_LWA_APP_ID = get_config("AMAZON_UK_LWA_APP_ID")
AMAZON_UK_LWA_CLIENT_SECRET = get_config("AMAZON_UK_LWA_CLIENT_SECRET")

AMAZON_US_REFRESH_TOKEN = get_config("AMAZON_US_REFRESH_TOKEN")
AMAZON_US_LWA_APP_ID = get_config("AMAZON_US_LWA_APP_ID")
AMAZON_US_LWA_CLIENT_SECRET = get_config("AMAZON_US_LWA_CLIENT_SECRET")

AWS_S3_ACCESS_KEY_ID = BUCKET_ACCESS_KEY
AWS_S3_SECRET_ACCESS_KEY = BUCKET_SECRET_KEY
AWS_S3_ENDPOINT_URL = f"https://{BUCKET_DOMAIN}"

PARCELHUB_API_USERNAME = get_config("PARCELHUB_API_USERNAME")
PARCELHUB_API_PASSWORD = get_config("PARCELHUB_API_PASSWORD")
PARCELHUB_API_ACCOUNT_ID = get_config("PARCELHUB_API_ACCOUNT_ID")

ShopifyAPISession.set_login(
    shop_url=SHOPIFY_SHOP_URL,
    api_version=SHOPIFY_API_VERSION,
    api_password=SHOPIFY_API_PASSWORD,
)

LinnworksAPISession.set_login(
    application_id=LINNAPI_APPLICATION_ID,
    application_secret=LINNAPI_APPLICATION_SECRET,
    application_token=LINNAPI_APPLICATION_TOKEN,
)

AmapiSessionUK.set_login(
    refresh_token=AMAZON_UK_REFRESH_TOKEN,
    app_id=AMAZON_UK_LWA_APP_ID,
    client_secret=AMAZON_UK_LWA_CLIENT_SECRET,
)

AmapiSessionUS.set_login(
    refresh_token=AMAZON_US_REFRESH_TOKEN,
    app_id=AMAZON_US_LWA_APP_ID,
    client_secret=AMAZON_US_LWA_CLIENT_SECRET,
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.postgres",
    "django.contrib.admin",
    "django.contrib.auth",
    "polymorphic",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_bootstrap5",
    "django_select2",
    "django_summernote",
    "storages",
    "adminsortable2",
    "easy_thumbnails",
    "imagekit",
    "file_exchange",
    "mathfilters",
    "solo",
    "formtools",
    "stcadmin",
    "home",
    "labelmaker",
    "inventory",
    "price_calculator",
    "django_markup",
    "jchart",
    "orders",
    "shipping",
    "fba",
    "channels",
    "purchases",
    "reports",
    "hardware",
    "linnworks",
    "restock",
    "hours",
    "logs",
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
        "DIRS": [SOURCE_DIR / "templates"],
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

STATICFILES_DIRS = [SOURCE_DIR / "stcadmin" / "static"]

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
        "order_profit_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "order_profit.log",
            "maxBytes": 1_048_576,
            "backupCount": 2,
            "formatter": "default_formatter",
            "delay": True,
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "stcadmin_error.log",
            "maxBytes": 1_048_576,
            "backupCount": 2,
            "level": "ERROR",
            "filters": ["add_user_to_log_record"],
            "formatter": "default_formatter",
        },
        "profit_loss_error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "profit_loss_error.log",
            "maxBytes": 1_048_576,
            "backupCount": 2,
            "level": "ERROR",
            "filters": ["add_user_to_log_record"],
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
        "linnworks_import_export": {
            "handlers": ["error_file_handler", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "product_creation": {
            "handlers": ["error_file_handler", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
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


class ManifestStaticFilesStorageForgiving(ManifestStaticFilesStorage):
    """Subclass ManifestStaticFilesStorage to ignore missing files."""

    manifest_strict = False

    def hashed_name(self, name, content=None, filename=None):
        """Ignore missing static files."""
        try:
            result = super().hashed_name(name, content, filename)
        except ValueError:
            result = name
        return result


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "stcadmin.settings.ManifestStaticFilesStorageForgiving",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DOCS_ROOT = SOURCE_DIR / "docs" / "build" / "html"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "home:index"

CELERY_BROKER_URL = get_config("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

SUMMERNOTE_THEME = "bs5"

SUMMERNOTE_CONFIG = {
    "iframe": False,
    "width": "100%",
    "toolbar": [
        ["font", ["bold", "underline", "italic", "strikethrough"]],
        ["text", ["superscript", "subscript", "clear"]],
        ["para", ["ul", "ol", "hr"]],
        ["table", ["table"]],
        ["view", ["fullscreen", "codeview"]],
        ["undo", ["undo", "redo"]],
    ],
}

THUMBNAIL_DEFAULT_STORAGE_ALIAS = "default"


class ProductImageStorage(S3Boto3Storage):
    """Storage class for product images."""

    bucket_name = get_config("PRODUCT_IMAGE_BUCKET")
    default_acl = "public-read"
    file_overwrite = True
    querystring_auth = False

    def _save(self, name, content):
        content.seek(0, os.SEEK_SET)
        with SpooledTemporaryFile() as content_autoclose:
            content_autoclose.write(content.read())
            return super(ProductImageStorage, self)._save(name, content_autoclose)


def imagekit_processor_namer(generator):
    """Return the filename for an image produced by django-imagekit."""
    source_filename = getattr(generator.source, "name", None)
    processor_name = "_".join(
        [processor.__class__.__name__.lower() for processor in generator.processors]
    )
    path = Path(source_filename)
    return f"{path.stem}_{processor_name}{path.suffix}"


class ImagekitDumbFileBackend(AbstractCacheFileBackend):
    """Cache backend for Imagekit that assumes images exist."""

    def generate(self, file, force=False):
        """Create an imagekit image."""
        self.generate_now(file, force=force)

    def generate_now(self, file, force=False):
        """Create an imagekit image."""
        file._generate()
        file.close()

    def exists(self, file):
        """Assume files exist."""
        return True


TESTING = (
    len(sys.argv) > 1
    and sys.argv[1] == "test"
    or os.path.basename(sys.argv[0]) in ("pytest", "py.test")
)


IMAGEKIT_DEFAULT_FILE_STORAGE = "stcadmin.settings.ProductImageStorage"
IMAGEKIT_DEFAULT_CACHEFILE_BACKEND = "stcadmin.settings.ImagekitDumbFileBackend"
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.Optimistic"
IMAGEKIT_CACHEFILE_DIR = ""
IMAGEKIT_SPEC_CACHEFILE_NAMER = "stcadmin.settings.imagekit_processor_namer"


if TESTING:
    MEDIA_ROOT = tempfile.mkdtemp()
    IMAGEKIT_DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
