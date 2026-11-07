from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ai.serializer import OllamaApiSerializer
from ai.service.geopy_generator import create_coordinates
from ai.service.ollama_generator import generate_route
from ai.service.valhalla_generator import engine_route


class OllamaAIViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OllamaApiSerializer

    @action(methods=["POST"], url_path="generate", url_name="generate", detail=False)
    def generate_route(self, request, *args, **kwargs):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        ollama = generate_route(request_serializer.validated_data)
        geopy = create_coordinates(ollama["way_points"])
        valhalla = engine_route(geopy)
        return Response(data={"valhalla": valhalla, "ollama": ollama}, status=status.HTTP_200_OK)
