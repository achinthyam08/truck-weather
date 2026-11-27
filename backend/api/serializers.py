from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers


class PlanRequestSerializer(serializers.Serializer):
    origin = serializers.CharField(max_length=200)
    destination = serializers.CharField(max_length=200)
    departure = serializers.DateTimeField()
    load_lb = serializers.FloatField(min_value=0, max_value=80_000)
    interval_miles = serializers.ChoiceField(choices=[10, 25, 50])

    def validate_departure(self, value):
        if value < timezone.now() - timedelta(hours=1):
            raise serializers.ValidationError("Departure cannot be in the past.")
        return value
