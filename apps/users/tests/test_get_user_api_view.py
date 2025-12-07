from typing import Any

import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from apps.users.api.views import UserMeApi

pytestmark = [pytest.mark.django_db]


def test_user_me_get_success(api_rf: Any, user_factory: Any) -> None:
    """Проверяет успешное получение профиля текущего пользователя.

    Arrange:
        - Создаем пользователя.
        - Формируем GET-запрос к /api/v1/users/me/.
        - Аутентифицируем запрос.

    Act:
        - Выполняем запрос через UserMeApi.

    Assert:
        - Проверяем HTTP статус 200 (OK).
        - Проверяем совпадение email.
    """
    email = 'exist@example.com'
    password = 'pwd123'
    user = user_factory(email=email, password=password)

    request = api_rf.get('/api/v1/users/me/')
    force_authenticate(request, user=user)
    view = UserMeApi.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('email') == email


def test_user_me_unauthorized(api_rf: Any) -> None:
    """Проверяет запрет доступа к профилю для анонимного пользователя.

    Arrange:
        - Формируем GET-запрос к /api/v1/users/me/ без аутентификации.

    Act:
        - Выполняем запрос.

    Assert:
        - Проверяем HTTP статус 401 или 403.
    """
    request = api_rf.get('/api/v1/users/me/')
    view = UserMeApi.as_view()

    response = view(request)

    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
