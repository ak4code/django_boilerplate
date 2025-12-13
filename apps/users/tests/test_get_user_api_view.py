from typing import Any

import pytest
from rest_framework import status
from rest_framework.test import APIClient


pytestmark = [pytest.mark.django_db]


def test_user_me_get_success(api_client: APIClient, user_factory: Any) -> None:
    """
    Проверяет успешное получение профиля текущего пользователя.

    Arrange:
        - Создаем пользователя.
        - Аутентифицируем клиента этим пользователем.
        - Готовим GET-запрос к /api/v1/users/me/.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Проверяем HTTP-статус 200 (OK).
        - Проверяем совпадение email в ответе.
    """
    user = user_factory(email='exist@example.com', password='pwd123')

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/v1/users/me/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get("email") == user.email


def test_user_me_unauthorized( api_client: APIClient) -> None:
    """
    Проверяет запрет доступа к профилю для анонимного пользователя.

    Arrange:
        - Не аутентифицируем клиента.
        - Готовим GET-запрос к /api/v1/users/me/.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Проверяем HTTP-статус 401 или 403.
    """
    response = api_client.get("/api/v1/users/me/")

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )
