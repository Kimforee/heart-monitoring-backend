# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # show extra fields in admin list display
    list_display = ("username", "email", "is_staff", "is_clinician")
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("phone", "is_clinician")}),
    )
