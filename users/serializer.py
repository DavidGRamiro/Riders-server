from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
            "email",
            "direccion",
            "telf",
            "carnet",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        extra_data = {"username": user.get_username(), "email": user.email, "is_active": True}
        data["extra_data"] = extra_data
        return data
