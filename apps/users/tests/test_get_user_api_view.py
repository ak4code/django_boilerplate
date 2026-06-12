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
        - Готовим GET-запрос к /api/users/me/.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Проверяем HTTP-статус 200 (OK).
        - Проверяем совпадение email в ответе.
    """
    user = user_factory(email='exist@example.com', password='pwd123')

    api_client.force_authenticate(user=user)
    response = api_client.get('/api/users/me/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('email') == user.email


def test_user_me_with_version_header(api_client: APIClient, user_factory: Any) -> None:
    """
    Проверяет работу версионирования API через заголовок Accept.

    Arrange:
        - Создаем пользователя и аутентифицируем клиента.
        - Готовим GET-запрос с заголовком Accept: application/json; version=v1.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Проверяем HTTP-статус 200 (OK) для поддерживаемой версии.
    """
    user = user_factory(email='versioned@example.com', password='pwd123')

    api_client.force_authenticate(user=user)
    response = api_client.get('/api/users/me/', HTTP_ACCEPT='application/json; version=v1')

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('email') == user.email


def test_user_me_with_unsupported_version_header(api_client: APIClient, user_factory: Any) -> None:
    """
    Проверяет отказ при запросе неподдерживаемой версии API в заголовке Accept.

    Arrange:
        - Создаем пользователя и аутентифицируем клиента.
        - Готовим GET-запрос с заголовком Accept: application/json; version=v999.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Проверяем HTTP-статус 406 (Not Acceptable).
    """
    user = user_factory(email='unsupported@example.com', password='pwd123')

    api_client.force_authenticate(user=user)
    response = api_client.get('/api/users/me/', HTTP_ACCEPT='application/json; version=v999')

    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


def test_user_me_unauthorized(api_client: APIClient) -> None:
    """
    Проверяет запрет доступа к профилю для анонимного пользователя.

    Arrange:
        - Не аутентифицируем клиента.
        - Готовим GET-запрос к /api/users/me/.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Проверяем HTTP-статус 401 или 403.
    """
    response = api_client.get('/api/users/me/')

    assert response.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )
