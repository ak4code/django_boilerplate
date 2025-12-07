from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.api.serializers import UserRegisterRequestSerializer, UserResponseSerializer
from apps.users.services import create_user


class UserRegisterApi(APIView):
    """API endpoint для регистрации новых пользователей."""

    permission_classes = [AllowAny]
    request_serializer = UserRegisterRequestSerializer
    response_serializer = UserResponseSerializer

    def post(self, request: Request) -> Response:
        """Обрабатывает POST запрос на регистрацию.

        1. Валидирует входящие данные через InputSerializer.
        2. Вызывает сервис создания пользователя.
        3. Возвращает созданного пользователя через OutputSerializer.

        :param request: Объект HTTP запроса.
        :return: HTTP ответ с данными пользователя или ошибками валидации.
        """
        serializer = self.request_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = create_user(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        except ValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        output_serializer = self.response_serializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class UserMeApi(APIView):
    """API endpoint для получения профиля текущего пользователя."""

    permission_classes = [IsAuthenticated]
    response_serializer = UserResponseSerializer

    def get(self, request: Request) -> Response:
        """Возвращает данные текущего авторизованного пользователя.

        :param request: Объект HTTP запроса.
        :return: HTTP ответ с данными профиля.
        """
        output_serializer = self.response_serializer(request.user)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
