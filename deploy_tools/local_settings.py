
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'NAME': 'stcadmin',
        'USER': 'stcadmin_django',
        'PASSWORD': 'DATABASE PASSWORD',
        'PORT': '5432',
    }
}

# SECURITY WARNING: don't run with debug turned on in production!

PYLINNWORKS_CONFIG = {
    "application_id": "APPLICATION_ID",
    "application_secret": "APPLICATION_SECRET",
    "application_token": "APPLICATION_TOKEN",
    "server": "https://api.linnworks.net//"
}

DEBUG = False
