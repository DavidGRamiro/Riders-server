from typing import TYPE_CHECKING, Any, cast

from django.contrib.auth import get_user_model, get_user
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

if TYPE_CHECKING:
    from users.models import User


class UserLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs) -> dict[str, Any]:
        data = cast(dict[str, Any], super().validate(attrs))
        user = self.user

        user.is_online = True
        user.save(update_fields=["is_online"])

        extra_data = {
            "username": user.get_username(),
            "email": user.email,
            "is_online": user.is_online,
            "authenticated": user.is_authenticated,
        }
        data["extra_data"] = extra_data
        return data


class RefreshUserTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        refresh = RefreshToken(attrs["refresh"])
        data = cast(dict[str, Any], super().validate(attrs))

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM)
        user = cast(
            "User",
            get_user_model().objects.get(**{api_settings.USER_ID_FIELD: user_id}),
        )

        data["extra_data"] = {
            "username": user.get_username(),
            "email": user.email,
            "is_online": user.is_online,
            "authenticated": user.is_authenticated,
        }
        return data
