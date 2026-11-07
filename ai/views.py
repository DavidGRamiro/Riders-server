from xml.dom import ValidationErr

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ai.exceptions import OllamaServiceException
from ai.serializer import OllamaApiSerializer, ResponseSerializer
from ai.service.geopy_generator import create_coordinates
from ai.service.ollama_generator import generate_route
from ai.service.valhalla_generator import engine_route
from routes.services.route_ai_generated import assign_route_to_user


class OllamaAIViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OllamaApiSerializer

    @action(methods=["POST"], url_path="generate", url_name="generate", detail=False)
    def generate_route(self, request, *args, **kwargs):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        try:
            ollama = generate_route(request_serializer.validated_data)
            geopy = create_coordinates(ollama["way_points"])
            route_engine = engine_route(geopy)

            response = {"ollama": ollama, "route_engine": route_engine}
            assign_route_to_user(self.request.user, response)

            serializer = ResponseSerializer(data=response)
            serializer.is_valid(raise_exception=True)
        except ValidationErr as ex:
            raise OllamaServiceException() from ex

        return Response(data=serializer.data, status=status.HTTP_200_OK)
