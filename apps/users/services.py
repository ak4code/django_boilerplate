from apps.users.models import User


def create_user(*, email: str, password: str) -> User:
    """
    Создает нового пользователя в системе.

    :param email: Email пользователя (используется как логин).
    :param password: Сырой пароль пользователя.
    :return: Экземпляр созданного пользователя.
    """
    return User.objects.create_user(email=email, password=password)
