# patients/serializers.py
from rest_framework import serializers
from .models import Patient, HeartRate
from django.utils import timezone

class PatientSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")

    class Meta:
        model = Patient
        fields = [
            "id",
            "owner",
            "first_name",
            "last_name",
            "date_of_birth",
            "sex",
            "place",
            "external_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("created_at", "updated_at")

from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Normal reading",
            value={"patient": 1, "bpm": 72, "recorded_at": "2025-09-20T10:00:00Z", "device_id": "device-abc"},
            request_only=True,
        )
    ]
)
class HeartRateSerializer(serializers.ModelSerializer):
    """
    Serializer for HeartRate reading. Validation enforces sensible `bpm` range
    and that `recorded_at` is a timezone-aware datetime (or naive treated as UTC).
    """
    class Meta:
        model = HeartRate
        fields = [
            "id",
            "patient",
            "bpm",
            "recorded_at",
            "device_id",
            "metadata",
            "created_at",
        ]
        read_only_fields = ("created_at",)

    def validate_bpm(self, value):
        # reasonable human heart rate bounds
        if value < 20 or value > 300:
            raise serializers.ValidationError("bpm must be between 20 and 300")
        return value

    def validate_recorded_at(self, value):
        # Do not allow future timestamps (small skew allowed)
        now = timezone.now()
        if value > now + timezone.timedelta(minutes=5):
            raise serializers.ValidationError("recorded_at cannot be in the far future")
        return value

    def validate(self, attrs):
        # ensure patient exists (ForeignKey enforces it) and other validations could go here
        return attrs
