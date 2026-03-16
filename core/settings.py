"""
Django settings for core project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from celery.schedules import crontab
import dj_database_url
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
HMAC_SECRET = os.getenv('HMAC_SECRET')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'confessions',
    'django_celery_beat',
    'moderator',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'confessions.middleware.AnonymousSessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'


DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
    )
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Celery ───────────────────────────────────────────────
CELERY_BROKER_URL      = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND  = 'redis://localhost:6379/0'
CELERY_TIMEZONE        = 'Asia/Kolkata'
CELERY_BEAT_SCHEDULER  = 'django_celery_beat.schedulers:DatabaseScheduler'

CELERY_BEAT_SCHEDULE = {

    # Runs every day at midnight
    'delete-expired-posts': {
        'task':     'confessions.tasks.delete_expired_posts',
        'schedule': crontab(hour=0, minute=0),
    },

    
    'highlight-weekly-kindness': {
        'task':     'confessions.tasks.highlight_weekly_kindness',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },

 
    'update-kindness-weeks': {
        'task':     'confessions.tasks.update_kindness_week_numbers',
        'schedule': crontab(hour=8, minute=55, day_of_week=1),
    },
}
