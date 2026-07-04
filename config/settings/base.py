from pathlib import Path
from decouple import config
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = 'django-insecure-c%f%u_8%lxutfg9hn+eo6xc+big=uhujt*p6ef7kh#_1)otvch'

DEBUG = True

ALLOWED_HOSTS = ['mentix.onrender.com', '*']

CSRF_TRUSTED_ORIGINS = [
    'https://c87089dbf506e1bd-84-94-248.serveousercontent.com',
]

AUTH_USER_MODEL = 'accounts.User'

DJANGO_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    'jazzmin',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'accounts',
    'common',
    'organizations',
    'patients',
    'appointments',
]

EXTERNAL_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'drf_yasg',
    'drf_spectacular',
    'django_filters',
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'static'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FRONTEND_URL = "https://zentaskob.uz"