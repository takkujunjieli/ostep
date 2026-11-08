from django.contrib.auth.models import User
from django.test import TestCase
from app.models import Ticket


class Smoke(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice")
        self.client.force_login(self.user)
        self.ticket = Ticket.objects.create(owner=self.user, title="Invoice", description="Broken button")

    def test_dashboard(self):
        self.assertContains(self.client.get("/"), "SupportDesk")

    def test_ticket_list(self):
        self.assertEqual(len(self.client.get("/api/tickets/").json()["tickets"]), 1)

    def test_create_endpoint_responds(self):
        response = self.client.post("/api/tickets/", {"title": "New", "description": "Problem"}, content_type="application/json")
        self.assertEqual(response.status_code, 201)
