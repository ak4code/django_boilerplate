from django.urls import path
from apps.users.api.views import UserRegisterApi, UserMeApi

app_name = 'users_api'
urlpatterns = [
    path('register/', UserRegisterApi.as_view(), name='register'),
    path('me/', UserMeApi.as_view(), name='me'),
]
