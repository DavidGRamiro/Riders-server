from rest_framework import serializers

from routes.enums.route_type import RouteTypes


class OllamaApiSerializer(serializers.Serializer):
    additional_message = serializers.CharField(
        max_length=200, required=False, help_text="Additional data that the user want"
    )
    route_type = serializers.ChoiceField(choices=RouteTypes, default=RouteTypes.RELAXED)
    distance_km = serializers.IntegerField(
        allow_null=True, required=False, help_text="Distance in kms"
    )
    duration_time = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="The duration time of the route. We always calculate de duration in minutes",
    )
    avoid_motorways = serializers.BooleanField(
        default=False,
        help_text="Avoid motorways and make the route in alternative way",
    )
    prefer_curvy_roads = serializers.BooleanField(default=True)
    origin = serializers.CharField(
        default="Madrid", max_length=100, help_text="Origin of the route"
    )
    destination = serializers.CharField(required=False)


class ResponseOllamaSerializer(serializers.Serializer):
    title = serializers.CharField()
    origin = serializers.CharField()
    destination = serializers.CharField()
    way_points = serializers.ListField()
    route_type = serializers.CharField()
    prefer_curvy_roads = serializers.BooleanField()
    distance_estimated_km = serializers.IntegerField()
