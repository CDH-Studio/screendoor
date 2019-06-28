"""
Django settings for screendoor_app project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from celery.schedules import crontab
from screendoor.NLP.NLPhelperfunctions import init_spacy_module

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

NLP_MODEL = init_spacy_module()
# Quick-start development settings - unsuitable for production
# See https://docs.d3jangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-t&#b2-=l%o=+a0-87weme6d&4pnn&$8a3x)v(my=yx7g5rp^s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    '/screendoor/static/',
]

# Email Authentication

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
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
        'schedule': crontab(minute=0, hour=14)
    },
    'delete_orphaned_positions': {
        'task': 'screendoor.tasks.delete_orphaned_positions',
        'schedule': crontab(minute=0, hour=14),
    }
}
