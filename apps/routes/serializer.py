from rest_framework import serializers

from apps.routes.models import Route, RouteGeneratedByUser


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"


class UserRouteGeneratedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteGeneratedByUser
        fields = "__all__"
