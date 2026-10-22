from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from users.exceptions import UserException
from users.models import User
from users.serializer import UserSerializer


def create_user_authenticate(data):
    """
    Create a new user and create new pairs of tokens.
    :param data: request data
    :return: Response with the user and pairs of tokens
    """
    try:
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return {
            "user": serializer.data,
            "token": str(refresh.access_token),
            "refresh": str(refresh),
        }
    except ValidationError as e:
        raise ValidationError(message=str(e))
