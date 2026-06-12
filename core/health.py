from django.db import connections
from django.http import HttpRequest, JsonResponse

from core.redis import get_redis


def health_check(request: HttpRequest) -> JsonResponse:
    """
    Проверяет работоспособность приложения и его зависимостей (БД, Redis).

    :param request: Объект HTTP запроса.
    :return: JSON со статусом каждого компонента; 503, если хоть один недоступен.
    """
    checks = {'database': True, 'redis': True}

    try:
        connections['default'].cursor().execute('SELECT 1')
    except Exception:  # noqa: BLE001
        checks['database'] = False

    try:
        get_redis().ping()
    except Exception:  # noqa: BLE001
        checks['redis'] = False

    healthy = all(checks.values())
    return JsonResponse(
        {'status': 'ok' if healthy else 'error', 'checks': checks},
        status=200 if healthy else 503,
    )
