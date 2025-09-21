# accounts/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


class AccountsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("account-register")
        self.token_url = "/api/auth/token/"
        self.profile_url = "/api/accounts/me/"

    def test_register_user_success(self):
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "complexpassword123",
        }
        resp = self.client.post(self.register_url, data=payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_with_short_password_fails(self):
        payload = {"username": "shortpw", "password": "123"}
        resp = self.client.post(self.register_url, data=payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("password", resp.data)

    def test_register_duplicate_username(self):
        User.objects.create_user(username="dup", password="pw12345678")
        payload = {"username": "dup", "password": "anotherpw123"}
        resp = self.client.post(self.register_url, data=payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_profile_requires_auth(self):
        resp = self.client.get(self.profile_url)
        self.assertEqual(resp.status_code, 401)

    def test_profile_returns_user(self):
        User.objects.create_user(
            username="me", password="pw12345678", email="me@example.com"
        )
        # obtain token
        token_resp = self.client.post(
            self.token_url, {"username": "me", "password": "pw12345678"}, format="json"
        )
        access = token_resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp = self.client.get(self.profile_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["username"], "me")
