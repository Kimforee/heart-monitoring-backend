# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom user model. For now it mirrors the default Django user but allows
    extension (roles, phone, organization) later without migrations headaches.
    """
    # example extra fields (optional)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_clinician = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.email})" if self.email else self.username
