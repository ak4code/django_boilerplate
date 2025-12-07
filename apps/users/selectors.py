from apps.users.models import User

def get_user_by_email(*, email: str) -> User | None:
    """
    Получает пользователя по email.

    :param email: Email для поиска.
    :return: Экземпляр пользователя или None, если не найден.
    """
    return User.objects.filter(email=email).first()
