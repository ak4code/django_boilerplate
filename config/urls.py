"""
URL configuration проекта.

Версионирование API реализовано через заголовок Accept (AcceptHeaderVersioning),
поэтому версия не входит в URL. Клиент указывает версию так:

    Accept: application/json; version=v1

Если заголовок не передан, используется версия по умолчанию (см. REST_FRAMEWORK
в config/settings/base.py).
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from config.views import health_check

api_urlpatterns = [
    path('users/', include('apps.users.api.urls', namespace='users_api')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('api/', include(api_urlpatterns)),
    # OpenAPI schema & docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
