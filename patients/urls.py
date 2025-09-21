# patients/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HeartRateViewSet, PatientViewSet

router = DefaultRouter()
router.register(r"patients", PatientViewSet, basename="patient")
router.register(r"heartrates", HeartRateViewSet, basename="heartrate")

urlpatterns = [
    path("", include(router.urls)),
]
