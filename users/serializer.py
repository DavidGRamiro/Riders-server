from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined',
            'email',
            'direccion',
            'telf',
            'carnet'
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
