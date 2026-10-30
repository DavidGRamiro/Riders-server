from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ai.serializer import OllamaApiSerializer
from ai.service.ollama_generator import generate_response


# Create your views here.
class OllamaAIViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OllamaApiSerializer

    @action(methods=["POST"], url_path="generate", url_name="generate", detail=False)
    def generate_route(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        ollama_response = generate_response(serializer.validated_data)
        return Response(data=ollama_response, status=status.HTTP_200_OK)
