from pathlib import Path

import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

if (BASE_DIR / '.env').exists():
    environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env.str('DJANGO_SECRET_KEY')

DEBUG = env.bool('DJANGO_DEBUG', default=False)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])

CSRF_TRUSTED_ORIGINS = env.list('DJANGO_CSRF_TRUSTED_ORIGINS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Dependency apps
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    # Local apps
    'apps.users',
]

MIDDLEWARE = [
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
}

_db_is_postgres = DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql'
if _db_is_postgres and env.bool('DJANGO_DB_POOL', default=True):
    # Нативный пул psycopg: пул несовместим с CONN_MAX_AGE и health checks Django
    DATABASES['default']['CONN_MAX_AGE'] = 0
    DATABASES['default']['CONN_HEALTH_CHECKS'] = False
    DATABASES['default'].setdefault('OPTIONS', {})['pool'] = {
        'min_size': env.int('DJANGO_DB_POOL_MIN_SIZE', default=2),
        'max_size': env.int('DJANGO_DB_POOL_MAX_SIZE', default=10),
        'timeout': env.int('DJANGO_DB_POOL_TIMEOUT', default=10),
    }
else:
    DATABASES['default']['CONN_MAX_AGE'] = env.int('DJANGO_DB_CONN_MAX_AGE', default=60)
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

# Argon2 — быстрее и устойчивее PBKDF2; остальные хэшеры нужны
# для прозрачной миграции уже существующих паролей
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = env.path('DJANGO_STATIC_ROOT', default=BASE_DIR / 'staticfiles')

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    # Версионирование API через заголовок Accept:
    #   Accept: application/json; version=v1
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ('v1',),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': env.str('DJANGO_THROTTLE_ANON', default='100/min'),
        'user': env.str('DJANGO_THROTTLE_USER', default='1000/min'),
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Boilerplate API',
    'DESCRIPTION': ('Версия API передаётся через заголовок Accept, например: `Accept: application/json; version=v1`.'),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env.str('REDIS_URL', default='redis://redis:6379/1'),
        'KEY_PREFIX': env.str('DJANGO_CACHE_KEY_PREFIX', default='app'),
        'OPTIONS': {
            # Параметры пула соединений redis-py
            'max_connections': env.int('REDIS_MAX_CONNECTIONS', default=100),
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30,
        },
    },
}

# Сессии в кэше с write-through в БД: чтение не нагружает PostgreSQL,
# при сбросе Redis сессии не теряются
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

EMAIL_TIMEOUT = env.int('DJANGO_EMAIL_TIMEOUT', default=10)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {module}:{lineno} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env.str('DJANGO_LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env.str('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        # Под нагрузкой 4xx-шум забивает логи: пишем только 5xx и медленные ответы
        'django.request': {
            'handlers': ['console'],
            'level': env.str('DJANGO_REQUEST_LOG_LEVEL', default='ERROR'),
            'propagate': False,
        },
    },
}

REDIS_HOST: str = env.str('REDIS_HOST', 'redis')
REDIS_PORT: int = env.int('REDIS_PORT', 6379)
REDIS_DB: int = env.int('REDIS_DB', 0)
REDIS_PASSWORD: str = env.str('REDIS_PASSWORD', None)
REDIS_DECODE_RESPONSES: bool = True
