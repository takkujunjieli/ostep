"""Instructor acceptance tests. All data and databases are temporary."""
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from shop.db import connect, initialize
from shop.service import OrderService, ShopError


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "shop.sqlite3"
        initialize(self.path)
        self.shop = OrderService(self.path, lambda: datetime(2026, 10, 24, 12, tzinfo=timezone.utc))

    def order(self, key="r1", customer="alice", sku="BOOK", quantity=1, discount=0):
        return self.shop.create_order(customer, key, [{"sku": sku, "quantity": quantity}], discount)

    def stock(self, sku="BOOK"):
        return next(p["stock"] for p in self.shop.products() if p["sku"] == sku)

    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(ShopError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_01_exact_stock_is_allowed(self):
        self.order(quantity=10)
        self.assertEqual(self.stock(), 0)

    def test_over_stock_is_rejected(self):
        self.error("OUT_OF_STOCK", self.order, quantity=11)
        self.assertEqual(self.stock(), 10)

    def test_duplicate_skus_are_aggregated(self):
        self.error("OUT_OF_STOCK", self.shop.create_order, "alice", "r1", [
            {"sku": "BOOK", "quantity": 6}, {"sku": "BOOK", "quantity": 5}])
        self.assertEqual(self.stock(), 10)

    def test_02_idempotency_keys_are_customer_scoped(self):
        alice = self.order()
        bob = self.order(customer="bob")
        self.assertNotEqual(alice["id"], bob["id"])
        self.assertEqual(bob["customer_id"], "bob")
        self.assertEqual(self.stock(), 8)

    def test_idempotency_payload_conflict(self):
        self.order()
        self.error("IDEMPOTENCY_CONFLICT", self.order, quantity=2)
        self.assertEqual(self.stock(), 9)

    def test_retry_normalizes_item_order(self):
        items = [{"sku": "BOOK", "quantity": 1}, {"sku": "PEN", "quantity": 2}]
        first = self.shop.create_order("alice", "r1", items)
        retry = self.shop.create_order("alice", "r1", list(reversed(items)))
        self.assertEqual(first, retry)

    def test_03_half_cent_rounds_up(self):
        self.assertEqual(self.order(sku="PEN", discount=50)["total_cents"], 51)

    def test_discount_rounds_once_for_entire_order(self):
        self.assertEqual(self.order(sku="PEN", quantity=3, discount=50)["total_cents"], 152)

    def test_full_discount_is_zero(self):
        self.assertEqual(self.order(discount=100)["total_cents"], 0)

    def test_04_equivalent_offset_matches_utc(self):
        order = self.order()
        found = self.shop.orders_between("alice", "2026-10-24T07:59:59-04:00", "2026-10-24T08:00:01-04:00")
        self.assertEqual([row["id"] for row in found], [order["id"]])

    def test_time_interval_is_half_open(self):
        self.order()
        self.assertEqual(len(self.shop.orders_between("alice", "2026-10-24T12:00:00Z", "2026-10-24T12:00:01Z")), 1)
        self.assertEqual(self.shop.orders_between("alice", "2026-10-24T11:00:00Z", "2026-10-24T12:00:00Z"), [])

    def test_naive_time_is_rejected(self):
        self.error("INVALID_TIME", self.shop.orders_between, "alice", "2026-10-24T12:00:00", "2026-10-25T12:00:00Z")

    def test_time_offsets_cross_calendar_day(self):
        self.order()
        self.assertEqual(len(self.shop.orders_between("alice", "2026-10-25T01:59:59+14:00", "2026-10-25T02:00:01+14:00")), 1)

    def test_05_pagination_never_repeats_boundary(self):
        expected = [self.order(key="r" + str(i))["id"] for i in range(5)]
        actual, cursor = [], 0
        for _ in range(10):
            page = self.shop.list_orders("alice", cursor, 2)
            actual.extend(order["id"] for order in page["orders"])
            if page["next_cursor"] is None:
                break
            cursor = page["next_cursor"]
        else:
            self.fail("Pagination did not terminate")
        self.assertEqual(actual, expected)

    def test_empty_page_has_no_cursor(self):
        self.assertEqual(self.shop.list_orders("alice"), {"orders": [], "next_cursor": None})

    def test_customer_isolation_in_order_list(self):
        self.order(customer="bob")
        self.assertEqual(self.shop.list_orders("alice")["orders"], [])

    def test_06_failed_order_rolls_back_earlier_stock_update(self):
        items = [{"sku": "BOOK", "quantity": 1}, {"sku": "ZZZ", "quantity": 1}]
        self.error("UNKNOWN_SKU", self.shop.create_order, "alice", "r1", items)
        self.assertEqual(self.stock(), 10)
        self.assertEqual(self.shop.list_orders("alice")["orders"], [])
        self.order()
        self.assertEqual(self.stock(), 9)

    def test_insufficient_later_item_rolls_back(self):
        items = [{"sku": "BOOK", "quantity": 1}, {"sku": "PEN", "quantity": 101}]
        self.error("OUT_OF_STOCK", self.shop.create_order, "alice", "r1", items)
        self.assertEqual(self.stock(), 10)

    def test_rejects_bad_quantities(self):
        for quantity in (0, -1, True, "1", 1.5, None):
            self.error("INVALID_INPUT", self.order, quantity=quantity)

    def test_rejects_bad_discounts(self):
        for discount in (-1, 101, True, 0.5, "50"):
            self.error("INVALID_INPUT", self.order, discount=discount)

    def test_rejects_invalid_pagination(self):
        for cursor, limit in ((-1, 10), (0, 0), (0, 101), (True, 2)):
            self.error("INVALID_INPUT", self.shop.list_orders, "alice", cursor, limit)

    def test_concurrent_retries_only_decrement_once(self):
        with ThreadPoolExecutor(max_workers=6) as pool:
            orders = list(pool.map(lambda _: self.order(), range(6)))
        self.assertEqual(len({order["id"] for order in orders}), 1)
        self.assertEqual(self.stock(), 9)

    def test_concurrent_buyers_cannot_oversell(self):
        def purchase(index):
            try:
                self.order(key="r" + str(index), quantity=6)
                return "ok"
            except ShopError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(purchase, range(2)))
        self.assertCountEqual(results, ["ok", "OUT_OF_STOCK"])
        self.assertEqual(self.stock(), 4)

    def test_persistence_survives_new_service_instance(self):
        original = self.order()
        reopened = OrderService(self.path)
        self.assertEqual(reopened.list_orders("alice")["orders"], [original])

    def test_failed_order_has_no_orphan_items(self):
        self.error("UNKNOWN_SKU", self.order, sku="ZZZ")
        connection = connect(self.path)
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM order_items").fetchone()[0], 0)
        finally:
            connection.close()
