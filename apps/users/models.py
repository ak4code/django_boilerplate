import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя, использующая email в качестве логина."""

    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(verbose_name='Email', unique=True, db_index=True)
    slug = models.CharField(
        verbose_name='Слаг страницы пользователя',
        blank=True,
        null=True,
        max_length=255,
        unique=True,
    )

    is_staff = models.BooleanField(verbose_name='Персонал', default=False)
    is_active = models.BooleanField(verbose_name='Активный', default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
