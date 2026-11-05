from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ai.serializer import OllamaApiSerializer, ResponseOllamaSerializer
from ai.service.ollama_generator import generate_and_save_route


class OllamaAIViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OllamaApiSerializer

    @action(methods=["POST"], url_path="generate", url_name="generate", detail=False)
    def generate_route(self, request, *args, **kwargs):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        route_data = generate_and_save_route(request_serializer.validated_data, request.user)

        response_serializer = ResponseOllamaSerializer(instance=route_data)
        return Response(data=response_serializer.data, status=status.HTTP_200_OK)
