from django.contrib.auth.models import User
from django.test import TestCase
from app.models import Actor


class Smoke(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice")
        self.client.force_login(self.user)
        self.actor = Actor.objects.create(name="Maya")

    def test_dashboard(self):
        self.assertContains(self.client.get("/"), "MovieDB")

    def test_empty_state(self):
        response = self.client.get("/api/state/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["unread_count"], 0)

    def test_follow_endpoint_responds(self):
        response = self.client.post(f"/api/actors/{self.actor.pk}/follow/", {}, content_type="application/json")
        self.assertEqual(response.status_code, 201)
