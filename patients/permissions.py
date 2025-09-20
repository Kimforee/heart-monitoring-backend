# patients/permissions.py
from rest_framework import permissions

class IsOwnerOrClinicianOrReadOnly(permissions.BasePermission):
    """
    - Read: allowed for authenticated users (you can restrict further if needed).
    - Write: allowed if user is owner of the patient (patient.owner) OR user.is_clinician OR user.is_staff.
    """
    def has_permission(self, request, view):
        # Ensure authenticated for all API access except you'd explicitly allow otherwise
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # obj can be Patient or HeartRate (heart_rate.patient)
        user = request.user
        if request.method in permissions.SAFE_METHODS:
            return True
        # Map if obj is HeartRate, check obj.patient.owner
        patient_owner = getattr(obj, "patient", None) or getattr(obj, "owner", None)
        # If obj is Patient, `patient_owner` is obj.owner (via getattr above)
        if hasattr(patient_owner, "owner") and not isinstance(patient_owner, (int, str)):
            # fallback
            pass
        # If patient_owner is a User instance:
        if patient_owner is None:
            return False
        # If patient_owner is a User model instance:
        try:
            owner_user = patient_owner if hasattr(patient_owner, "pk") else None
        except Exception:
            owner_user = None

        # allow if user is staff or clinician
        if user.is_staff or getattr(user, "is_clinician", False):
            return True

        # allow if user is owner_user
        if owner_user and owner_user == user:
            return True

        return False
