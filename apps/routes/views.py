from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.routes.models import Route, RouteGeneratedByUser
from apps.routes.serializer import RouteSerializer, UserRouteGeneratedSerializer


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]


class RouteGeneratedByUserViewSet(ModelViewSet):
    queryset = RouteGeneratedByUser.objects.none()
    serializer_class = UserRouteGeneratedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RouteGeneratedByUser.objects.filter(id_fk_user=self.request.user)
