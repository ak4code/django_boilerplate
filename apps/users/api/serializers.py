from rest_framework import serializers
from apps.users.models import User

class UserRegisterRequestSerializer(serializers.Serializer):
    """Сериализатор для валидации входящих данных при регистрации."""

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict) -> dict:
        """
        Проверяет совпадение паролей.

        :param attrs: Словарь валидированных атрибутов.
        :return: Словарь атрибутов, если проверка пройдена.
        :raise serializers.ValidationError: Если пароли не совпадают.
        """
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return attrs


class UserResponseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для формирования ответа с данными пользователя.
    Исключает чувствительные данные (пароли, права доступа).
    """
    class Meta:
        model = User
        fields = ('uuid', 'email', 'date_joined', 'is_active')
