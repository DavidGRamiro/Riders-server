from rest_framework import serializers

from routes.enums.route_type import RouteTypes


class OllamaApiSerializer(serializers.Serializer):
    additional_message = serializers.CharField(
        max_length=200, required=False, help_text="Additional data that the user want"
    )
    route_type = serializers.ChoiceField(choices=RouteTypes, default=RouteTypes.RELAXED)
    distance_km = serializers.IntegerField(default=5, help_text="Distance in kms")
    duration_time = serializers.IntegerField(
        default=0,
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
    response = serializers.CharField()
    role = serializers.CharField()
    done = serializers.BooleanField()
    total_duration = serializers.IntegerField()
