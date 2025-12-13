from django.conf import settings
from redis import Redis

_redis_client: Redis | None = None


def get_redis() -> Redis:
    """
    Возвращает общий Redis-клиент.

    :return: экземпляр Redis
    :raises RuntimeError: если клиент не может быть создан
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=settings.REDIS_DECODE_RESPONSES,
        )

    return _redis_client
