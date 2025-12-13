# Единый HTTP-слой на APIView

## Цели

- Единообразный стиль реализации HTTP-слоя.  
- Прозрачное разделение обязанностей между APIView и доменным слоем (services/selectors).  
- Упрощение чтения и сопровождения кода для всей команды.

***

## Почему APIView

В проекте используется единый подход: все HTTP-эндпоинты реализуются на базе `rest_framework.views.APIView`, а не через Function-Based Views или GenericViewSet/ModelViewSet.

Плюсы такого подхода:

- Явный и предсказуемый жизненный цикл запроса (`dispatch`, `get/post/...`).  
- Полный контроль над тем, как вызываются сериализаторы, сервисы и селекторы.  
- Отсутствие скрытой магии generic-классов, проще читать и отлаживать код.  
- Единый паттерн для всех разработчиков - меньше когнитивной нагрузки при переходе между модулями.

***

## Общие правила для APIView

1. Один публичный HTTP-метод - одна основная операция (например, `post` для создания, `get` для получения).  
2. В APIView запрещено:
   - Писать бизнес-логику.  
   - Работать напрямую с моделями (кроме простых случаев чтения id из URL).  
   - Дублировать логику валидации данных, уже реализованную в сериализаторах или сервисах.  

3. В APIView разрешено и рекомендуется:
   - Делегировать доменную логику в `services` и `selectors`.  
   - Использовать сериализаторы только для валидации входных данных и формирования ответа.  
   - Обрабатывать только HTTP-аспекты: статус-коды, формат ответа, маппинг исключений.

***

## Структура APIView

Каждый метод (`get`, `post`, `put`, `patch`, `delete`) логически делится на 4 шага:

1. Извлечение и валидация входных данных (`RequestSerializer` / query params / path params).  
2. Вызов селектора/сервиса.  
3. Преобразование результата в `ResponseSerializer`.  
4. Формирование `Response` с корректным HTTP-статусом.

Пример шаблона:

```python
from typing import Any

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import UserRegisterRequestSerializer, UserResponseSerializer
from apps.users.services import create_user


class UserRegisterApi(APIView):
    """
    Регистрация нового пользователя.
    """

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Обрабатывает POST-запрос на регистрацию пользователя.

        :param request: HTTP-запрос
        :return: HTTP-ответ с данными пользователя или ошибкой
        """
        # 1. Валидация входа
        serializer = UserRegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Вызов сервиса
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

        # 3. Сериализация результата
        output_serializer = UserResponseSerializer(user)

        # 4. Формирование ответа
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )
```

***

## Требования к сериализаторам для APIView

Для единообразия:

- Используются отдельные сериализаторы для:
  - входных данных: `*RequestSerializer`,  
  - выходных данных: `*ResponseSerializer`, если это оправдано.  
- APIView не должна "догадываться", какие поля можно принимать, это описано в `RequestSerializer`.  
- APIView не должна собирать response-JSON вручную - это обязанность `ResponseSerializer`.

***

## Тестирование APIView

- Для всех APIView пишутся интеграционные тесты через `APIClient`.  
- Структура тестов:
  - docstring в формате AAA (Arrange / Act / Assert).  
  - Проверка:
    - кодов ответов,  
    - структуры и содержания ответа,  
    - взаимодействия с сервисами (при необходимости через моки).  

Пример:

```python
from typing import Any

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

## Организация кода в приложении

Рекомендуемая структура модуля приложения:

```text
apps/
  users/
    api/
      views.py             # APIView-контроллеры
      serializers.py       # Request/Response сериализаторы
      urls.py              # Роутинг API
    services.py            # Бизнес-логика (изменение состояния)
    selectors.py           # Чтение и выборки
    models.py
    tests/
      test_api_*.py
      test_services_*.py
      test_selectors_*.py
```