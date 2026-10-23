from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

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
            "is_online",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        user.id_online = True
        user.save(update_fields=["id_online"])

        extra_data = {
            "username": user.get_username(),
            "email": user.email,
            "is_online": user.is_online,
        }
        data["extra_data"] = extra_data
        return data
