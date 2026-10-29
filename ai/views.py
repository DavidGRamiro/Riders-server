from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.serializer import OllamaApiSerializer
from ai.service.ollama_generator import generate_response


# Create your views here.
class OllamaAI(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request, *args, **kwargs):
        serializer = OllamaApiSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = generate_response(serializer.validated_data)
        return Response(data=response.message.content, status=status.HTTP_200_OK)
