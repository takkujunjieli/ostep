from django.contrib.auth.models import User
from django.test import TestCase
from app.models import Reply, Ticket


class Acceptance(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice")
        self.bob = User.objects.create_user("bob")
        self.admin = User.objects.create_user("admin", is_staff=True)
        self.client.force_login(self.alice)
        self.ticket = Ticket.objects.create(owner=self.alice, title="Invoice download fails", description="PDF error")

    def post(self, path, data=None):
        return self.client.post(path, data or {}, content_type="application/json")

    def test_01_new_ticket_is_saved_and_owned(self):
        response = self.post("/api/tickets/", {"title": "New", "description": "Problem"})
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.json()["id"])
        self.assertTrue(Ticket.objects.filter(pk=response.json()["id"], owner=self.alice).exists())

    def test_02_reply_route_reaches_service(self):
        response = self.post(f"/api/tickets/{self.ticket.pk}/replies/", {"body": "More details"})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Reply.objects.filter(ticket=self.ticket, author=self.alice, body="More details").exists())

    def test_03_thread_includes_support_agent_replies(self):
        Reply.objects.create(ticket=self.ticket, author=self.alice, body="Customer")
        Reply.objects.create(ticket=self.ticket, author=self.admin, body="Agent")
        response = self.client.get(f"/api/tickets/{self.ticket.pk}/")
        self.assertEqual([row["body"] for row in response.json()["replies"]], ["Customer", "Agent"])

    def test_04_closed_status_survives_reload(self):
        response = self.post(f"/api/tickets/{self.ticket.pk}/close/")
        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "closed")
        self.assertEqual(self.client.get(f"/api/tickets/{self.ticket.pk}/").json()["status"], "closed")

    def test_05_search_is_partial_and_case_insensitive(self):
        other = Ticket.objects.create(owner=self.bob, title="Invoice secret", description="Private")
        response = self.client.get("/api/tickets/", {"q": "  INVOICE  "})
        self.assertEqual([row["id"] for row in response.json()["tickets"]], [self.ticket.pk])
        self.assertNotIn(other.pk, [row["id"] for row in response.json()["tickets"]])

    def test_guard_ticket_visibility(self):
        self.client.force_login(self.bob)
        self.assertEqual(self.client.get(f"/api/tickets/{self.ticket.pk}/").status_code, 404)
        self.assertEqual(self.client.get("/api/tickets/").json()["tickets"], [])

    def test_guard_reply_cannot_target_another_customer(self):
        # Call the service to check authorization independently of the reply URL task.
        from app.services import reply_to_ticket
        from core import Problem
        with self.assertRaises(Problem) as error:
            reply_to_ticket(self.bob, self.ticket.pk, "Unauthorized")
        self.assertEqual(error.exception.status, 404)
        self.assertEqual(Reply.objects.count(), 0)

    def test_guard_closed_ticket_rejects_reply(self):
        from app.services import reply_to_ticket
        from core import Problem
        self.ticket.status = "closed"
        self.ticket.save()
        with self.assertRaises(Problem) as error:
            reply_to_ticket(self.alice, self.ticket.pk, "Late")
        self.assertEqual(error.exception.code, "TICKET_CLOSED")

    def test_guard_blank_title_rejected(self):
        self.assertEqual(self.post("/api/tickets/", {"title": "  ", "description": "Problem"}).status_code, 400)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_guard_agent_can_view_customer_ticket(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(f"/api/tickets/{self.ticket.pk}/").status_code, 200)
