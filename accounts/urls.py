# accounts/urls.py
from django.urls import path

from .views import ProfileView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="account-register"),
    path("me/", ProfileView.as_view(), name="account-me"),
]
