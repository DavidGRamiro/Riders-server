from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.bikes.models import Bike
from apps.bikes.serializer import BikeSerializer


class MotorcycleViewSet(viewsets.ModelViewSet):
    queryset = Bike.objects.all()
    serializer_class = BikeSerializer
    permission_classes = [IsAuthenticated]
