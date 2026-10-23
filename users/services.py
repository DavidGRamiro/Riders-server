from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

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

        user = serializer.save(date_joined=timezone.now())
        refresh = RefreshToken.for_user(user)
        return {
            "user": serializer.data,
            "token": str(refresh.access_token),
            "refresh": str(refresh),
        }
    except ValidationError as e:
        raise ValidationError(message=str(e))
