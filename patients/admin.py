# patients/admin.py
from django.contrib import admin
from .models import Patient, HeartRate

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "external_id", "owner", "created_at")
    search_fields = ("first_name", "last_name", "external_id", "owner__username")
    list_filter = ("place",)

@admin.register(HeartRate)
class HeartRateAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "bpm", "recorded_at", "device_id")
    search_fields = ("patient__first_name", "patient__last_name", "device_id")
    list_filter = ("device_id",)
