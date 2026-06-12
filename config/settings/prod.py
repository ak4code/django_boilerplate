# Production settings
DEBUG = False

# Healthcheck Docker/k8s ходит изнутри контейнера на 127.0.0.1 по HTTP
if '127.0.0.1' not in ALLOWED_HOSTS:  # noqa: F821
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, '127.0.0.1']  # noqa: F821
SECURE_REDIRECT_EXEMPT = [r'^health/$']

# Приложение работает за обратным прокси (nginx/traefik), который терминирует TLS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)  # noqa: F821

SECURE_HSTS_SECONDS = env.int('DJANGO_SECURE_HSTS_SECONDS', default=60 * 60 * 24 * 30)  # noqa: F821
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'

# Манифестное хранилище статики: хэши в именах файлов + сжатие
STORAGES['staticfiles']['BACKEND'] = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # noqa: F821

# В production браузерные формы DRF не нужны
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)  # noqa: F821

# Количество прокси перед приложением — для корректного определения IP клиента
# в троттлинге (X-Forwarded-For)
REST_FRAMEWORK['NUM_PROXIES'] = env.int('DJANGO_NUM_PROXIES', default=1)  # noqa: F821
