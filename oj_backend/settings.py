from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = open(BASE_DIR / 'secret.key', 'r').read()

MODE = os.getenv('OJ_MODE', 'DEVELOPMENT').upper()

SQL_DATA = {
    i: os.getenv(f'OJ_SQL_{i}', j)
    for i, j in [
        ('HOST', 'localhost'),
        ('PORT', '5432'),
        ('USER', ''),
        ('PASSWORD', ''),
        ('NAME', 'oj'),
    ]
}

if MODE == 'PRODUCTION':
    DEBUG = False
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            **SQL_DATA,
        },
    }
elif MODE == 'TEST':
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            **SQL_DATA,
        },
    }
else:
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

ALLOW_REGISTER = os.getenv('OJ_ALLOW_REGISTER', 'TRUE').upper() == 'TRUE'

ALLOWED_HOSTS = ['*']

VENDOR_APPS = [
    # 'channels',
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
    'oj_contest.apps.ContestConfig',
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
# ASGI_APPLICATION = 'oj_backend.asgi.application'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

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

STATIC_ROOT = BASE_DIR / 'static'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'oj_user.User'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'oj_backend.permissions.IsAuthenticatedAndReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oj_backend.authentication.SessionAuthentication',
    ],
    'EXCEPTION_HANDLER':
    'oj_backend.utils.exception_handler',
}

SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/login/',
    'LOGOUT_URL': '/admin/logout/',
}

CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_BROKER_URL = 'amqp://127.0.0.1:5672'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': ['redis://127.0.0.1:6379/2'],
        }
    }
}

JUDGE_SERVER = '127.0.0.1:8080'
JUDGE_DATA_ROOT = BASE_DIR / 'judge_data'
SUBMISSION_ROOT = JUDGE_DATA_ROOT / 'submission'
TEST_DATA_ROOT = JUDGE_DATA_ROOT / 'test_data'
SPJ_ROOT = JUDGE_DATA_ROOT / 'spj'
