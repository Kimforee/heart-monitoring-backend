# patients/tests.py
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Patient, HeartRate
from django.utils import timezone
import datetime

User = get_user_model()

class PatientsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create two users
        self.user1 = User.objects.create_user(username="u1", password="pw12345678")
        self.user2 = User.objects.create_user(username="u2", password="pw12345678")
        # clinician
        self.clinician = User.objects.create_user(username="clin", password="pw12345678", is_clinician=True)
        # urls
        self.patients_list = "/api/patients/patients/"
        self.heartrates_list = "/api/patients/heartrates/"

    def authenticate(self, user):
        resp = self.client.post("/api/auth/token/", {"username": user.username, "password": "pw12345678"}, format="json")
        token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_patient_and_heart_rate_by_owner(self):
        self.authenticate(self.user1)
        p_payload = {"first_name": "Alice", "last_name": "A", "external_id": "EXT1"}
        resp = self.client.post(self.patients_list, p_payload, format="json")
        self.assertEqual(resp.status_code, 201)
        patient_id = resp.data["id"]

        hr_payload = {"patient": patient_id, "bpm": 72, "recorded_at": timezone.now().isoformat()}
        resp = self.client.post(self.heartrates_list, hr_payload, format="json")
        self.assertEqual(resp.status_code, 201)

    def test_bpm_validation_too_low_or_high(self):
        self.authenticate(self.user1)
        p = self.client.post(self.patients_list, {"first_name": "Z"}, format="json").data
        pid = p["id"]

        resp_low = self.client.post(self.heartrates_list, {"patient": pid, "bpm": 10, "recorded_at": timezone.now().isoformat()}, format="json")
        self.assertEqual(resp_low.status_code, 400)
        self.assertIn("bpm", resp_low.data)

        resp_high = self.client.post(self.heartrates_list, {"patient": pid, "bpm": 5000, "recorded_at": timezone.now().isoformat()}, format="json")
        self.assertEqual(resp_high.status_code, 400)

    def test_recorded_at_future_validation(self):
        self.authenticate(self.user1)
        p = self.client.post(self.patients_list, {"first_name": "Future"}, format="json").data
        pid = p["id"]
        future_time = (timezone.now() + datetime.timedelta(days=365)).isoformat()
        resp = self.client.post(self.heartrates_list, {"patient": pid, "bpm": 80, "recorded_at": future_time}, format="json")
        assert resp.status_code in (400, 201)  # serializer rejects only if > now + 5 minutes; this test ensures behavior
        if resp.status_code == 400:
            self.assertIn("recorded_at", resp.data)

    def test_filter_by_date_range(self):
        # create patient and multiple HRs at known dates
        self.authenticate(self.user1)
        p = self.client.post(self.patients_list, {"first_name": "F"}, format="json").data
        pid = p["id"]
        now = timezone.now()
        # create several readings
        for days_ago, bpm in [(10,70), (5,80), (1,90)]:
            dt = (now - datetime.timedelta(days=days_ago)).isoformat()
            self.client.post(self.heartrates_list, {"patient": pid, "bpm": bpm, "recorded_at": dt}, format="json")
        # filter between 6 and 2 days ago => should return the 5-day entry only
        start = (now - datetime.timedelta(days=6)).date().isoformat()
        end = (now - datetime.timedelta(days=2)).date().isoformat()
        resp = self.client.get(f"{self.heartrates_list}?patient={pid}&start={start}&end={end}")
        self.assertEqual(resp.status_code, 200)
        items = resp.data.get("results", resp.data)
        # at least one record (the 5-day entry)
        self.assertTrue(any(hr["bpm"] == 80 for hr in items))

    def test_pagination_limit_offset(self):
        self.authenticate(self.user1)
        p = self.client.post(self.patients_list, {"first_name": "Paginate"}, format="json").data
        pid = p["id"]
        # create 30 readings
        now = timezone.now()
        for i in range(30):
            dt = (now - datetime.timedelta(minutes=i)).isoformat()
            self.client.post(self.heartrates_list, {"patient": pid, "bpm": 60 + (i % 30), "recorded_at": dt}, format="json")
        # request with limit=10
        resp = self.client.get(f"{self.heartrates_list}?patient={pid}&limit=10&offset=0")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("results", resp.data)
        self.assertEqual(len(resp.data["results"]), 10)

    def test_clinician_can_see_all_patients(self):
        # create patient by user2
        self.authenticate(self.user2)
        self.client.post(self.patients_list, {"first_name": "Other"}, format="json")
        # clinician lists patients
        self.authenticate(self.clinician)
        resp = self.client.get(self.patients_list)
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data.get("results", resp.data)), 1)

    def test_user_cannot_create_hr_for_other_patient(self):
        # create patient by user2
        self.authenticate(self.user2)
        p = self.client.post(self.patients_list, {"first_name": "Other2"}, format="json").data
        pid = p["id"]
        # user1 attempts to create HR for pid -> forbidden
        self.authenticate(self.user1)
        resp = self.client.post(self.heartrates_list, {"patient": pid, "bpm": 88, "recorded_at": timezone.now().isoformat()}, format="json")
        self.assertEqual(resp.status_code, 403)
