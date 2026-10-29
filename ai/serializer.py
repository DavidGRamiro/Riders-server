from rest_framework import serializers


class OllamaApiSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, max_length=200)
