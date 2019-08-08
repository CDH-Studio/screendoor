"""
Django settings for screendoor_app project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import ast
from celery.schedules import crontab
from screendoor.NLP.helpers.load_nlp import init_spacy_module
from configparser import RawConfigParser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SCREENDOOR_SECRET_KEY', 'abdef')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ast.literal_eval(os.getenv('DEBUG', 'True'))

NLP_MODEL = init_spacy_module()
# Quick-start development settings - unsuitable for production
# See https://docs.d3jangoproject.com/en/2.2/howto/deployment/checklist/

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ScreenDoor
    'screendoor.apps.ScreenDoorConfig',
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

ROOT_URLCONF = 'screendoor_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'screendoor_app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'screendoor_db',
        'USER': 'cdhstudio',
        'PASSWORD': 'cdhadmin',
        'HOST': 'db',
        'PORT': 5432,
    }
}

# Session Management
# SESSION_ENGINE = [
#    'django.contrib.sessions.backends.cached_db',
# ]

# User Management
AUTH_USER_MODEL = 'screendoor.ScreenDoorUser'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Toronto'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "/static/")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# Email Authentication

# Email Setup
config = RawConfigParser()
config.read('settings.ini')
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = config.get('email', 'EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config.get('email', 'EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
PASSWORD_RESET_TIMEOUT_DAYS = 1

# Security

# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# File Uploads

# FILE_UPLOAD_HANDLERS = (
#     "django.core.files.uploadhandler.TemporaryFileUploadHandler",)

# FILE_UPLOAD_TEMP_DIR = ("/code/screendoor/temp")
MEDIA_URL = 'code/screendoor/temp/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'code/screendoor/temp')
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o644
# FILE_UPLOAD_MAX_MEMORY_SIZE = 0
# MEDIA_ROOT = ("/code/screendoor/temp")

# Celery Settings

CELERY_BROKER_URL = 'pyamqp://rabbitmq:rabbitmq@rabbitmq:5672'
CELERY_RESULT_BACKEND = 'rpc://'
CELERYD_STATE_DB = '/tmp/celery_state'

CELERY_BEAT_SCHEDULE = {
    'delete_authorization_tokens': {
        'task': 'screendoor.tasks.delete_authorization_tokens',
        'schedule': crontab(hour="*/1")
    },
    'delete_orphaned_positions': {
        'task': 'screendoor.tasks.delete_orphaned_positions',
        'schedule': crontab(hour="*/1")
    }
}
