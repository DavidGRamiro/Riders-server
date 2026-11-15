from rest_framework import serializers

from apps.routes.enums.route_type import RouteTypes


class OllamaApiSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    way_points = serializers.ListField(required=False)
    distance_estimated_km = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    way_points_coords = serializers.ListField(required=False)
    additional_message = serializers.CharField(
        max_length=500, required=False, help_text="Additional data that the user want"
    )
    route_type = serializers.ChoiceField(choices=RouteTypes, default=RouteTypes.RELAXED)
    avoid_motorways = serializers.BooleanField(
        default=True,
        help_text="Avoid motorways and make the route in alternative way",
    )
    prefer_curvy_roads = serializers.BooleanField(default=True)
    origin = serializers.CharField(
        default="Madrid", max_length=100, help_text="Origin of the route"
    )
    destination = serializers.CharField(required=False, allow_null=True)


class CoordinatesSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lon = serializers.FloatField()


class ValhallaSerializer(serializers.Serializer):
    distance = serializers.FloatField()
    duration = serializers.FloatField()
    coordinates = CoordinatesSerializer(many=True)


class ResponseSerializer(serializers.Serializer):
    ollama = OllamaApiSerializer()
    route_engine = ValhallaSerializer()
