# accounts/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Read-only user serializer used for responses."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "phone", "is_clinician", "is_staff")


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration. Accepts password and creates a user
    with set_password. Username is required by default.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "phone")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user
