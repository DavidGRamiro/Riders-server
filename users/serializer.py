from rest_framework import serializers

from users.models import User, UserGeneratedRoute


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


class UserRouteGeneratedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGeneratedRoute
        fields = "__all__"
