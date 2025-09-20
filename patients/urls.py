# patients/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PatientViewSet, HeartRateViewSet

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"heartrates", HeartRateViewSet, basename="heartrate")

urlpatterns = [
    path("", include(router.urls)),
]
