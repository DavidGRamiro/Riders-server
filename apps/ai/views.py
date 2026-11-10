from xml.dom import ValidationErr

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.ai.exceptions import OllamaServiceException
from apps.ai.serializer import OllamaApiSerializer, ResponseSerializer
from apps.ai.service.ollama_generator import (
    engine_route_generator,
)


class OllamaAIViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OllamaApiSerializer

    @action(methods=["POST"], url_path="generate", url_name="generate", detail=False)
    def generate_route(self, request, *args, **kwargs):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        try:
            response = engine_route_generator(request_serializer.validated_data, request.user)
            serializer = ResponseSerializer(data=response)
            serializer.is_valid(raise_exception=True)
            return Response(data=serializer.validated_data, status=status.HTTP_200_OK)
        except ValidationErr as ex:
            raise OllamaServiceException() from ex

        return Response(data=serializer.data, status=status.HTTP_200_OK)
