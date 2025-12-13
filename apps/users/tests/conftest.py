from collections.abc import Callable
from typing import Any

import pytest
from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """
    Фикстура для клиента API.

    :return: экземпляр APIClient для выполнения HTTP-запросов в тестах
    """
    return APIClient()


@pytest.fixture
def user_factory(
    db: Any,
    django_user_model: type[AbstractBaseUser],
) -> Callable[..., AbstractBaseUser]:
    """
    Фикстура-фабрика для создания пользователей в тестах.

    :param db: фикстура базы данных pytest-django
    :param django_user_model: модель пользователя, предоставляемая pytest-django
    :return: функция make_user(**kwargs) для создания пользователя
    """

    def make_user(
        email: str = "user@example.com",
        password: str = "password",
        **extra: Any,
    ) -> AbstractBaseUser:
        """
        Создать пользователя через django_user_model.

        :param email: email пользователя
        :param password: пароль пользователя
        :param extra: дополнительные именованные поля модели
        :return: созданный объект пользователя
        """
        return django_user_model.objects.create_user(
            email=email,
            password=password,
            **extra,
        )

    return make_user
