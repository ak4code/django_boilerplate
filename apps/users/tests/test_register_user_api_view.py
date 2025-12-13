from typing import Any

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = [pytest.mark.django_db]


def test_user_register_success(
    api_client: APIClient,
) -> None:
    """
    Проверяет успешную регистрацию пользователя.

    Arrange:
        - Подготавливаем валидные данные (email, совпадающие пароли).
        - Формируем POST-запрос к /api/v1/users/register/.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Проверяем HTTP-статус 201 (Created).
        - Проверяем, что возвращенный email соответствует переданному.
    """
    email = "newuser@example.com"
    password = "strongpassword"
    payload = {
        "email": email,
        "password": password,
        "confirm_password": password,
    }

    response = api_client.post(
        "/api/v1/users/register/",
        data=payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data.get('email') == email


def test_user_register_service_validation_error(
    api_client: APIClient,
    mocker: Any,
) -> None:
    """
    Проверяет обработку ошибки бизнес-логики (ValidationError).

    Arrange:
        - Подготавливаем данные для регистрации.
        - Мокаем сервисный слой create_user на выброс ошибки.
        - Формируем POST-запрос к /api/v1/users/register/.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Проверяем HTTP-статус 400 (Bad Request).
        - Проверяем наличие сообщения об ошибке.
    """
    mock_create_user = mocker.patch(
        "apps.users.api.views.create_user",
    )
    mock_create_user.side_effect = ValidationError('User already exists')

    password = "strongpassword"
    payload = {
        "email": "bad@example.com",
        "password": password,
        "confirm_password": password,
    }

    response = api_client.post(
        "/api/v1/users/register/",
        data=payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'User already exists' in response.data.get('detail')


def test_user_register_password_mismatch(
    api_client: APIClient,
) -> None:
    """
    Проверяет валидацию несовпадающих паролей на уровне сериализатора.

    Arrange:
        - Подготавливаем данные с разными паролями.
        - Формируем запрос к /api/v1/users/register/.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Проверяем HTTP-статус 400 (Bad Request).
    """
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password456",
    }

    response = api_client.post(
        "/api/v1/users/register/",
        data=payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
