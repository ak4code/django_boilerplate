## Общие правила для docstring и комментариев

- В теле функций и тестов использовать одинарные кавычки `'...'`, кроме docstring.  
- Многострочный docstring:
  - Открывающие `"""` на отдельной строке.  
  - Со следующей строки - краткое описание.  

Пример:

```python
def do_something(x: int) -> int:
    """
    Делает что-то с числом.

    :param x: входное значение
    :return: результат обработки
    """
    result = x + 1
    return result
```

## Docstring для обычного кода

- Не использовать AAA.  
- Использовать reST-нотацию с `:param`, `:return`, `:raises` при необходимости.  
- Если функция ничего не возвращает, `:return` можно опускать.  
- Если функция может выбрасывать исключения - документировать через `:raises`.

Пример сервиса:

```python
def create_user(email: str, password: str) -> User:
    """
    Создает нового пользователя в системе.

    :param email: адрес электронной почты пользователя
    :param password: пароль пользователя в открытом виде
    :return: созданный пользователь
    :raises ValueError: если email уже занят или некорректен
    """
    if not email:
        raise ValueError('Email is required')

    user = User.objects.create_user(email=email, password=password)
    return user
```

## Комментарии в коде

- Не писать комментарии для очевидных вещей.  
- Комментарии добавляются только по отдельному запросу или для пояснения нетривиальной логики.  
- Предпочтение - чистый код и качественные docstring вместо обилия комментариев.

## Кавычки

- В теле функций и тестов - одинарные кавычки `'...'`.  
- В docstring - тройные двойные кавычки `"""..."""`.

## Docstring для тестов

- Всегда использовать формат AAA:
  - `Arrange:` - подготовка данных и окружения.  
  - `Act:` - одно действие, которое тестируется.  
  - `Assert:` - проверки результата.  
- Описание теста кратко формулирует, что именно проверяется.

Пример:

```python
def test_user_me_get_success(api_client: APIClient, user_factory: Any) -> None:
    """
    Проверяет успешное получение профиля текущего пользователя.

    Arrange:
        - Создаем пользователя.
        - Аутентифицируем клиента.

    Act:
        - Выполняем GET-запрос к /api/v1/users/me/.

    Assert:
        - Проверяем статус 200.
        - Проверяем, что email в ответе совпадает с ожидаемым.
    """
    email = 'user@example.com'
    user = user_factory(email=email, password='password123')

    api_client.force_authenticate(user=user)
    response = api_client.get('/api/v1/users/me/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == email
```