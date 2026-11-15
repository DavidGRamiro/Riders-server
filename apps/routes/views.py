from typing import Any

from rest_framework import filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
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
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "prompt"]
    ordering_fields = ["id"]

    def get_queryset(self):
        user = self.request.user
        queryset = RouteGeneratedByUser.objects.filter(id_fk_user=user)
        return queryset

    def destroy(self, request, *args, **kwargs):
        route = self.get_object()
        route.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
