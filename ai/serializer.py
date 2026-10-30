from rest_framework import serializers

from routes.enums.route_type import RouteTypes


class OllamaApiSerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=200, required=False, help_text="Additional data that the user wont"
    )
    route_type = serializers.ChoiceField(choices=RouteTypes, default=RouteTypes.RELAXED)
    distance = serializers.IntegerField(required=False, min_value=5, help_text="Distance in kms")
    duration_time = serializers.IntegerField(
        required=False,
        min_value=60,
        help_text="The duration time of the route. We always calculate de duration in minutes",
    )
    without_traffic = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether the route without traffic should be ignored",
    )
