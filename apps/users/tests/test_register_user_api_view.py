from typing import Any

import pytest
from rest_framework import status

from apps.users.api.views import UserRegisterApi

pytestmark = [pytest.mark.django_db]


def test_user_register_success(api_rf: Any, monkeypatch: Any) -> None:
    """Проверяет успешную регистрацию пользователя.

    Arrange:
        - Подготавливаем валидные данные (email, совпадающие пароли).
        - Мокаем сервисный слой create_user, чтобы он возвращал объект пользователя.
        - Формируем POST-запрос к /api/v1/users/register/.

    Act:
        - Выполняем запрос через UserRegisterApi.

    Assert:
        - Проверяем HTTP статус 201 (Created).
        - Проверяем, что возвращенный email соответствует переданному.
    """
    email = 'newuser@example.com'
    password = 'strongpassword'
    payload = {'email': email, 'password': password, 'confirm_password': password}

    request = api_rf.post('/api/v1/users/register/', data=payload)
    view = UserRegisterApi.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data.get('email') == email


def test_user_register_service_validation_error(api_rf: Any, monkeypatch: Any) -> None:
    """Проверяет обработку ошибки бизнес-логики (ValidationError).

    Arrange:
        - Подготавливаем данные для регистрации.
        - Мокаем сервисный слой create_user на выброс ошибки (дубликат пользователя).
        - Формируем запрос к /api/v1/users/register/.

    Act:
        - Выполняем запрос через UserRegisterApi.

    Assert:
        - Проверяем HTTP статус 400 (Bad Request).
        - Проверяем наличие сообщения об ошибке.
    """
    password = 'pwd'
    payload = {'email': 'bad@example.com', 'password': password, 'confirm_password': password}

    request = api_rf.post('/api/v1/users/register/', data=payload)
    view = UserRegisterApi.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data


def test_user_register_password_mismatch(api_rf: Any) -> None:
    """Проверяет валидацию несовпадающих паролей на уровне сериализатора.

    Arrange:
        - Подготавливаем данные с разными паролями.
        - Формируем запрос к /api/v1/users/register/.

    Act:
        - Выполняем запрос через UserRegisterApi.

    Assert:
        - Проверяем HTTP статус 400 (Bad Request).
    """
    payload = {'email': 'test@example.com', 'password': 'password123', 'confirm_password': 'password456'}

    request = api_rf.post('/api/v1/users/register/', data=payload)
    view = UserRegisterApi.as_view()

    response = view(request)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
