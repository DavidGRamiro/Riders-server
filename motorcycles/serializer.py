from rest_framework import serializers
from motorcycles.models import Motorcycle


class MotorcycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motorcycle
        fields = '__all__'