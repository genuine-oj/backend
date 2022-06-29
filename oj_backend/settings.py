from pathlib import Path
import os
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = open(BASE_DIR / 'secret.key', 'r').read()

PRODUCTION = os.getenv('MODE', 'development').lower() == 'production'

if PRODUCTION:
    DEBUG = False
    ALLOWED_HOSTS = []
else:
    DEBUG = True
    ALLOWED_HOSTS = ['*']

VENDOR_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'drf_yasg',
]

LOCAL_APPS = [
    'oj_user.apps.UserConfig',
    'oj_problem.apps.ProblemConfig',
    'oj_submission.apps.SubmissionConfig',
]

INSTALLED_APPS = VENDOR_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'oj_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'oj_backend.wsgi.application'

if PRODUCTION:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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

LANGUAGE_CODE = 'en'

LOCALE_PATHS = [BASE_DIR / 'locale']

LANGUAGES = [
    ('en', 'English'),
    ('zh-Hans', '中文简体'),
]

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'oj_user.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'oj_backend.permissions.IsAuthenticatedAndReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oj_backend.authentication.SessionAuthentication',
    ],
    'EXCEPTION_HANDLER': 'oj_backend.utils.exception_handler',
}

SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/login/',
    'LOGOUT_URL': '/admin/logout/',
}

CELERY_TIMEZONE = TIME_ZONE

CELERY_ACCEPT_CONTENT = ['json']

CELERY_TASK_SERIALIZER = 'json'

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'

CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

JUDGE_SERVER = '127.0.0.1:18082'

JUDGE_DATA_ROOT = BASE_DIR / 'judge_data'

TEST_DATA_ROOT = JUDGE_DATA_ROOT / 'test_data'

SPJ_ROOT = JUDGE_DATA_ROOT / 'spj'
