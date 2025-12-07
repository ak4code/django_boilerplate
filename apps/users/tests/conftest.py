from typing import TYPE_CHECKING, Any, Callable

import pytest

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    from rest_framework.test import APIRequestFactory


@pytest.fixture
def api_rf() -> 'APIRequestFactory':
    from rest_framework.test import APIRequestFactory

    return APIRequestFactory()


@pytest.fixture
def user_factory() -> Callable[..., 'AbstractBaseUser']:
    """Фабрика для создания пользователей через модель пользователя."""
    from django.contrib.auth import get_user_model

    def make_user(email: str = 'user@example.com', password: str = 'password') -> Any:
        # Получаем модель внутри функции, чтобы избежать ранней инициализации
        UserModel = get_user_model()
        return UserModel.objects.create_user(email=email, password=password)

    return make_user
