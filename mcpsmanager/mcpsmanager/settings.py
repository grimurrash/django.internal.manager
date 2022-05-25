"""
Django settings for mcpsmanager project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os.path
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

env = environ.Env(DEBUG=(bool, False))

environ.Env.read_env(os.path.join(ROOT_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'https://api.telegram.org',
    'http://localhost:3000',
    'http://localhost:8000',
    'http://localhost:8080',
    'http://localhost:8081',
)
# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'helpdesk.apps.HelpdeskConfig',
    'teamsevent',
    'botcollection.apps.BotcollectionConfig',
    'corsheaders',
    'eventtimeline.apps.EventTimelineConfig',
    'museumregistration.apps.MuseumRegistrationConfig',
    'answerstoquestions',
    'eventregistration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'mcpsmanager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'mcpsmanager.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env.str('MANAGER_DATABASE_ENGINE'),
        'HOST': env.str('MANAGER_DATABASE_HOST'),
        'PORT': env.str('MANAGER_DATABASE_PORT'),
        'NAME': env.str('MANAGER_DATABASE_NAME'),
        'USER': env.str('MANAGER_DATABASE_USER'),
        'PASSWORD': env.str('MANAGER_DATABASE_PASSWORD'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static/'
UPLOADS_ROOT = os.path.join(BASE_DIR, 'uploads/')
UPLOADS_URL = '/uploads/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# microsoft auth
MICROSOFT_APP_CLIENT_ID = env('MICROSOFT_APP_CLIENT_ID')
MICROSOFT_APP_CLIENT_SECRET = env('MICROSOFT_APP_CLIENT_SECRET')
MICROSOFT_APP_TENANT_ID = env('MICROSOFT_APP_TENANT_ID')

# google auth
GOOGLE_CREDENTIALS_FILE_PATH = os.path.join(ROOT_DIR, env('GOOGLE_CREDENTIALS_FILE'))

# google tables
GOOGLE_HELPDESK_SPREADSHEET_ID = env('GOOGLE_HELPDESK_SPREADSHEET_ID')
GOOGLE_CHECKLIST_SPREADSHEET_ID = env('GOOGLE_CHECKLIST_SPREADSHEET_ID')
GOOGLE_MUSEUMREGISTRATION_SPREADSHEET_ID = env('GOOGLE_MUSEUMREGISTRATION_SPREADSHEET_ID')

# google folders
GOOGLE_MUSEUMREGISTRATION_DOCUMENTS_FOLDER_ID = env('GOOGLE_MUSEUMREGISTRATION_DOCUMENTS_FOLDER_ID')

# HELP DESK SETTING
TELEGRAM_MCPSIT_BOT_TOKEN = env('TELEGRAM_MCPSIT_BOT_TOKEN')
