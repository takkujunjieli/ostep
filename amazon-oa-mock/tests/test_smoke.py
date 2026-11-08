import tempfile
import unittest
from pathlib import Path

from shop.db import initialize
from shop.service import OrderService


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.sqlite3"
        initialize(self.path)
        self.shop = OrderService(self.path)

    def test_catalog(self):
        self.assertEqual(len(self.shop.products()), 3)

    def test_create_order(self):
        order = self.shop.create_order("alice", "r1", [{"sku": "BOOK", "quantity": 1}])
        self.assertEqual(order["total_cents"], 1299)
        self.assertEqual(self.shop.list_orders("alice")["orders"][0]["id"], order["id"])

    def test_same_retry(self):
        args = ("alice", "r1", [{"sku": "BOOK", "quantity": 1}])
        self.assertEqual(self.shop.create_order(*args), self.shop.create_order(*args))
        book = next(p for p in self.shop.products() if p["sku"] == "BOOK")
        self.assertEqual(book["stock"], 9)

    def test_whole_cent_discount(self):
        order = self.shop.create_order("alice", "r1", [{"sku": "PEN", "quantity": 10}], 10)
        self.assertEqual(order["total_cents"], 909)
