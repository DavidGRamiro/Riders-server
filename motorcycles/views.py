from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated

from motorcycles.models import Motorcycle
from motorcycles.serializer import MotorcycleSerializer


class MotorcycleViewSet(viewsets.ModelViewSet):
    queryset = Motorcycle.objects.all()
    serializer_class = MotorcycleSerializer
    permission_classes = [IsAuthenticated]