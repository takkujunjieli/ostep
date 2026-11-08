from django.contrib.auth.models import User
from django.test import TestCase
from app.models import Wallet


class Smoke(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice")
        Wallet.objects.create(user=self.user, balance_cents=10000)
        self.client.force_login(self.user)

    def test_dashboard(self):
        self.assertContains(self.client.get("/"), "Wallet")

    def test_balance(self):
        self.assertEqual(self.client.get("/api/state/").json()["balance_cents"], 10000)

    def test_empty_history(self):
        self.assertEqual(self.client.get("/api/history/").json(), {"transfers": []})
