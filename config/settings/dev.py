# Development settings
DEBUG = env.bool('DJANGO_DEBUG', default=True)  # noqa: F821

if not ALLOWED_HOSTS:  # noqa: F821
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Whitenoise отдаёт статику напрямую из finders без collectstatic
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True

# Локальная разработка без Redis: кэш в памяти процесса
if env.bool('DJANGO_USE_LOCMEM_CACHE', default=False):  # noqa: F821
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
    }
