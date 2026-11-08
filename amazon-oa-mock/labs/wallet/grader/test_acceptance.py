from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from app.models import Transfer, Wallet
from app.services import transfer_money


class Acceptance(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice")
        self.bob = User.objects.create_user("bob")
        self.charlie = User.objects.create_user("charlie")
        self.a = Wallet.objects.create(user=self.alice, balance_cents=10000)
        self.b = Wallet.objects.create(user=self.bob, balance_cents=5000)
        Wallet.objects.create(user=self.charlie, balance_cents=0)
        self.client.force_login(self.alice)

    def post(self, amount=250, recipient="bob"):
        return self.client.post("/api/transfers/", {"recipient": recipient, "amount_cents": amount}, content_type="application/json")

    def test_01_documented_transfer_route_exists(self):
        self.assertEqual(self.post().status_code, 201)
        self.assertEqual(Transfer.objects.count(), 1)

    def test_02_transfer_credits_recipient_and_conserves_total(self):
        transfer_money(self.alice, "bob", 250)
        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.assertEqual((self.a.balance_cents, self.b.balance_cents), (9750, 5250))
        self.assertEqual(self.a.balance_cents + self.b.balance_cents, 15000)

    def test_03_history_includes_incoming_and_excludes_other_users(self):
        incoming = Transfer.objects.create(sender=self.a, recipient=self.b, amount_cents=250)
        self.client.force_login(self.bob)
        rows = self.client.get("/api/history/").json()["transfers"]
        self.assertEqual([row["id"] for row in rows], [incoming.pk])
        self.assertEqual(rows[0]["direction"], "incoming")
        self.client.force_login(self.charlie)
        self.assertEqual(self.client.get("/api/history/").json()["transfers"], [])

    def test_04_exact_balance_transfer_succeeds(self):
        transfer_money(self.alice, "bob", 10000)
        self.a.refresh_from_db()
        self.assertEqual(self.a.balance_cents, 0)

    def test_05_ledger_failure_rolls_back_both_balances(self):
        with patch("app.services.Transfer.objects.create", side_effect=RuntimeError("Ledger unavailable")):
            with self.assertRaises(RuntimeError):
                transfer_money(self.alice, "bob", 250)
        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.assertEqual((self.a.balance_cents, self.b.balance_cents), (10000, 5000))
        self.assertEqual(Transfer.objects.count(), 0)

    def test_guard_insufficient_funds_has_no_side_effect(self):
        from core import Problem
        with self.assertRaises(Problem) as error:
            transfer_money(self.alice, "bob", 10001)
        self.assertEqual(error.exception.code, "INSUFFICIENT_FUNDS")
        self.a.refresh_from_db()
        self.assertEqual(self.a.balance_cents, 10000)
        self.assertEqual(Transfer.objects.count(), 0)

    def test_guard_amount_validation(self):
        from core import Problem
        for value in (0, -1, True, "250", 1.5, None):
            with self.assertRaises(Problem):
                transfer_money(self.alice, "bob", value)
        self.assertEqual(Transfer.objects.count(), 0)

    def test_guard_self_transfer_rejected(self):
        from core import Problem
        with self.assertRaises(Problem) as error:
            transfer_money(self.alice, "alice", 250)
        self.assertEqual(error.exception.code, "SELF_TRANSFER")

    def test_guard_unknown_recipient(self):
        from core import Problem
        with self.assertRaises(Problem) as error:
            transfer_money(self.alice, "missing", 250)
        self.assertEqual(error.exception.status, 404)
        self.a.refresh_from_db()
        self.assertEqual(self.a.balance_cents, 10000)

    def test_guard_login_required(self):
        self.client.logout()
        self.assertEqual(self.client.get("/api/history/").status_code, 401)
