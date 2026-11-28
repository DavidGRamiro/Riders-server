from django.core.serializers import get_serializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.bikes.models import Bike
from apps.bikes.serializer import BikeSerializer
from apps.bikes.services.bikes import create_user_bike


class MotorcycleViewSet(viewsets.ModelViewSet):
    queryset = Bike.objects.all()
    serializer_class = BikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            bike = create_user_bike(user, serializer.validated_data)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(
            status=status.HTTP_201_CREATED, data={"msg": "Nueva montura creada correctamente"}
        )
