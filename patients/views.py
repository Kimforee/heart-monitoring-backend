# patients/views.py
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import HeartRate, Patient
from .permissions import IsOwnerOrClinicianOrReadOnly
from .serializers import HeartRateSerializer, PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    /api/patients/patients/
    - list: returns patients owned by curr user, unless user.is_clinician or is_staff -> returns all
    - create: sets owner=request.user
    - retrieve/update/destroy: permission enforced (owner/staff/clinician)
    """

    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinicianOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_staff or getattr(user, "is_clinician", False):
            # clinician/staff can see all patients; allow optional filtering
            qs = qs
        else:
            qs = qs.filter(owner=user)
        # optional filtering by external_id or place via query params
        external_id = self.request.query_params.get("external_id")
        place = self.request.query_params.get("place")
        if external_id:
            qs = qs.filter(external_id=external_id)
        if place:
            qs = qs.filter(place__icontains=place)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HeartRateViewSet(viewsets.ModelViewSet):
    """
    /api/patients/heartrates/
    - list: supports filtering by patient (id), start_date, end_date, device_id
    - create: enforces that only owner / clinician / staff can create for a patient
    - retrieve: available
    """

    serializer_class = HeartRateSerializer
    queryset = HeartRate.objects.select_related("patient").all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinicianOrReadOnly]

    def get_queryset(self):
        qs = self.queryset
        params = self.request.query_params

        patient_id = params.get("patient")
        device_id = params.get("device_id")
        start = params.get("start")  # ISO date or datetime
        end = params.get("end")

        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if device_id:
            qs = qs.filter(device_id=device_id)

        # parse start/end as datetime or date
        if start:
            dt = parse_datetime(start) or parse_date(start)
            if dt:
                # normalize date -> start of day, datetime -> direct
                if isinstance(dt, timezone.datetime) and dt.tzinfo is None:
                    dt = timezone.make_aware(dt, timezone.utc)
                if isinstance(dt, timezone.date) and not isinstance(
                    dt, timezone.datetime
                ):
                    dt = timezone.make_aware(
                        timezone.datetime.combine(dt, timezone.datetime.min.time()),
                        timezone.utc,
                    )
                qs = qs.filter(recorded_at__gte=dt)
        if end:
            dt = parse_datetime(end) or parse_date(end)
            if dt:
                if isinstance(dt, timezone.datetime) and dt.tzinfo is None:
                    dt = timezone.make_aware(dt, timezone.utc)
                if isinstance(dt, timezone.date) and not isinstance(
                    dt, timezone.datetime
                ):
                    dt = timezone.make_aware(
                        timezone.datetime.combine(dt, timezone.datetime.max.time()),
                        timezone.utc,
                    )
                qs = qs.filter(recorded_at__lte=dt)

        # If user is not clinician/staff, restrict to heart rates of patients they own
        user = self.request.user
        if not (user.is_staff or getattr(user, "is_clinician", False)):
            qs = qs.filter(patient__owner=user)

        return qs

    def perform_create(self, serializer):
        patient = serializer.validated_data.get("patient")
        user = self.request.user
        # If patient has an owner and it's not the user and user not clinician/staff -> deny
        if (
            patient.owner
            and patient.owner != user
            and not (user.is_staff or getattr(user, "is_clinician", False))
        ):
            raise PermissionDenied(
                "You are not allowed to add readings for this patient."
            )
        serializer.save()
