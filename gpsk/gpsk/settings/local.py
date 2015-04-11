from base import *

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gpsk-dev',
        'USER': 'user-dev',
        'PASSWORD': 'pass-dev',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    BASE_DIR.child('static'),
)