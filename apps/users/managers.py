from typing import Any

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер для создания пользователей с email в качестве логина."""

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> Any:
        """
        Создаёт и сохраняет пользователя с указанным email и паролем.

        :param email: email пользователя
        :param password: пароль пользователя или None
        :param extra_fields: дополнительные поля модели
        :return: созданный объект пользователя
        :raises ValueError: если email не указан
        """
        if not email:
            raise ValueError('Email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> Any:
        """
        Создаёт и сохраняет суперпользователя.

        :param email: email суперпользователя
        :param password: пароль суперпользователя или None
        :param extra_fields: дополнительные поля модели
        :return: созданный объект суперпользователя
        :raises ValueError: если is_staff или is_superuser не установлены в True
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
