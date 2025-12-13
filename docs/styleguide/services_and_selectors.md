# Services и Selectors в Django/DRF

## Цели

- Явное разделение чтения и изменения состояния.  
- Упрощение тестирования и повторного использования логики.  
- "Тонкие" контроллеры (APIView/ViewSet), "толстый" домен (services/selectors).

***

## Selectors

### Назначение

Selectors отвечают только за чтение данных:

- Не изменяют состояние БД (никаких `.save()`, `.create()`, `.delete()`).  
- Инкапсулируют логику выборок и оптимизации запросов (фильтры, `select_related`, `prefetch_related`).  
- Возвращают:
  - `QuerySet`,  
  - конкретные модели,  
  - DTO/словари/агрегированные структуры.

### Пример

```python
# apps/users/selectors.py

from typing import Iterable

from django.db.models import QuerySet

from apps.users.models import User


def get_active_users() -> QuerySet[User]:
    """
    Возвращает queryset активных пользователей.
    """
    return User.objects.filter(is_active=True)


def get_user_by_email(email: str) -> User | None:
    """
    Возвращает пользователя по email или None.

    :param email: адрес электронной почты
    :return: пользователь или None, если не найден
    """
    return User.objects.filter(email=email).first()
```

***

## Services

### Назначение

Services отвечают за изменение состояния и бизнес-правила:

- Создание, обновление, удаление сущностей.  
- Внешние интеграции (HTTP-клиенты, email/SMS, очереди задач).  
- Доменные проверки и бизнес-валидация (ограничения, workflow).

APIView не должна содержать бизнес-логику; она вызывает сервис и мапит результат в HTTP-ответ.

### Пример

```python
# apps/users/services.py

from django.core.exceptions import ValidationError

from apps.users.models import User


def create_user(email: str, password: str) -> User:
    """
    Создает нового пользователя.

    :param email: адрес электронной почты
    :param password: пароль пользователя в открытом виде
    :return: созданный пользователь
    :raises ValidationError: если пользователь с таким email уже существует
    """
    if User.objects.filter(email=email).exists():
        raise ValidationError('User with this email already exists')

    user = User.objects.create_user(email=email, password=password)
    return user
```

***

## Связка APIView → Services/Selectors

### Принципы

APIView/ViewSet выполняет только:

- Авторизацию, permissions, throttling.  
- Валидацию входа через сериализатор.  
- Вызов нужного `service` или `selector`.  
- Превращение результата в сериализатор/JSON.  
- Маппинг исключений домена в HTTP-коды.

### Пример APIView

```python
# apps/users/api/views.py

from typing import Any

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import UserRegisterInputSerializer, UserOutputSerializer
from apps.users.services import create_user


class UserRegisterApi(APIView):
    """
    Регистрация нового пользователя.
    """

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Обрабатывает POST-запрос на регистрацию.

        :param request: HTTP-запрос
        :return: HTTP-ответ с данными пользователя или ошибкой
        """
        serializer = UserRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
            )
        except ValidationError as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output = UserOutputSerializer(user)
        return Response(output.data, status=status.HTTP_201_CREATED)
```

***

## Тестирование

### Selectors

- Чистые unit-тесты без HTTP.  
- Проверяем:
  - корректность фильтров и результата,  
  - количество запросов (при необходимости),  
  - граничные случаи (нет записей, несколько записей).

Пример:

```python
def test_get_active_users_returns_only_active_users(django_user_model) -> None:
    """
    Проверяет, что возвращаются только активные пользователи.

    Arrange:
        - Создаем активного и неактивного пользователей.

    Act:
        - Вызываем get_active_users.

    Assert:
        - В результирующем queryset только активные пользователи.
    """
    django_user_model.objects.create_user(email='a@example.com', password='pwd', is_active=True)
    django_user_model.objects.create_user(email='b@example.com', password='pwd', is_active=False)

    qs = get_active_users()

    emails = {u.email for u in qs}
    assert emails == {'a@example.com'}
```

### Services

- Unit-тесты на уровне Python/ORM.  
- Мокаем внешние интеграции.  
- Проверяем:
  - эффект в БД,  
  - выбрасываемые исключения,  
  - вызовы внешних сервисов.

Пример:

```python
def test_create_user_success(django_user_model) -> None:
    """
    Проверяет успешное создание пользователя.

    Arrange:
        - Подготавливаем email и пароль.

    Act:
        - Вызываем create_user.

    Assert:
        - Пользователь создается в БД.
    """
    email = 'test@example.com'
    password = 'pwd123'

    user = create_user(email=email, password=password)

    assert user.email == email
    assert django_user_model.objects.filter(email=email).exists()
```

### APIView

- Интеграционные тесты через `APIClient`.  
- Проверяем:
  - auth/permissions,  
  - 200/201 vs 400/401/403/409,  
  - маппинг исключений сервиса в HTTP.  
- При необходимости мокаем `services` в негативных сценариях.

Пример:

```python
from rest_framework import status
from rest_framework.test import APIClient


def test_user_register_success(api_client: APIClient) -> None:
    """
    Проверяет успешную регистрацию пользователя.

    Arrange:
        - Подготавливаем валидные данные.
        - Формируем POST-запрос к /api/v1/users/register/.

    Act:
        - Выполняем запрос через APIClient.

    Assert:
        - Статус 201.
        - Email в ответе совпадает с переданным.
    """
    payload = {
        'email': 'new@example.com',
        'password': 'pwd123',
        'confirm_password': 'pwd123',
    }

    response = api_client.post(
        '/api/v1/users/register/',
        data=payload,
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['email'] == 'new@example.com'
```

***

## Структура проекта

Рекомендуемая структура для каждого приложения:

```text
apps/
  users/
    api/
      views.py
      serializers.py
      urls.py
    services.py
    selectors.py
    models.py
    tests/
      test_api_*.py
      test_services_*.py
      test_selectors_*.py
```

- `api/` – HTTP-слой (DRF).  
- `services.py` – изменение состояния и бизнес-логика.  
- `selectors.py` – чтение и выборки.  
- `tests/` разделяются по тем же слоям.