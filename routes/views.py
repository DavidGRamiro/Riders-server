from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from routes.models import Route
from routes.serializer import RouteSerializer


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]
