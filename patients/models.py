# patients/models.py
from django.db import models
from django.conf import settings

class Patient(models.Model):
    """
    Represents a patient monitored by the devices.
    """
    # who added/owns this patient (clinician or user)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="patients"
    )

    # core patient fields
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, blank=True)  # 'M','F','Other' or free text
    place = models.CharField(max_length=255, blank=True)  # optional place/ward/room

    external_id = models.CharField(max_length=128, blank=True, null=True,
                                   help_text="Optional external identifier (device/patient id)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["external_id"]),
            models.Index(fields=["owner"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip() + (f" ({self.external_id})" if self.external_id else "")

class HeartRate(models.Model):
    """
    Heart rate reading record for a patient.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="heart_rates")
    bpm = models.PositiveSmallIntegerField()  # beats per minute
    recorded_at = models.DateTimeField()  # when the reading was taken
    device_id = models.CharField(max_length=128, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True, help_text="Optional additional data from device")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-recorded_at",)
        indexes = [
            models.Index(fields=["patient", "recorded_at"]),
            models.Index(fields=["recorded_at"]),
        ]

    def __str__(self):
        return f"{self.patient} — {self.bpm} bpm at {self.recorded_at.isoformat()}"
