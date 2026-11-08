import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from .db import connect


class ShopError(Exception):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code = code
        self.status = status


def parse_time(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("timezone required")
        return parsed.astimezone(timezone.utc)
    except (ValueError, AttributeError, TypeError):
        raise ShopError("INVALID_TIME", "Use an ISO-8601 timestamp with timezone")


def normalized_time(value):
    return parse_time(value).isoformat(timespec="microseconds")


def discounted_total(subtotal, discount_percent):
    amount = Decimal(subtotal) * (100 - discount_percent) / 100
    return int(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def required_text(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ShopError("INVALID_INPUT", label + " must be non-empty text (max 200)")
    return value


class OrderService:
    def __init__(self, db_path, clock=None):
        self.db_path = db_path
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def products(self):
        connection = connect(self.db_path)
        try:
            return [dict(row) for row in connection.execute(
                "SELECT * FROM products ORDER BY sku")]
        finally:
            connection.close()

    def create_order(self, customer_id, request_key, items, discount_percent=0):
        required_text(customer_id, "customer_id")
        required_text(request_key, "request_key")
        if type(discount_percent) is not int or not 0 <= discount_percent <= 100:
            raise ShopError("INVALID_INPUT", "discount_percent must be an integer 0..100")
        if not isinstance(items, list) or not items:
            raise ShopError("INVALID_INPUT", "items must be a non-empty list")
        quantities = {}
        for item in items:
            if not isinstance(item, dict):
                raise ShopError("INVALID_INPUT", "Each item must be an object")
            sku = required_text(item.get("sku"), "sku")
            quantity = item.get("quantity")
            if type(quantity) is not int or quantity <= 0:
                raise ShopError("INVALID_INPUT", "quantity must be a positive integer")
            quantities[sku] = quantities.get(sku, 0) + quantity
        fingerprint = hashlib.sha256(json.dumps(
            [sorted(quantities.items()), discount_percent], separators=(",", ":")
        ).encode()).hexdigest()
        connection = connect(self.db_path)
        try:
            # Serialize writers before checking retries or inventory.
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT * FROM orders WHERE customer_id = ? AND request_key = ?",
                (customer_id, request_key),
            ).fetchone()
            if existing:
                if existing["fingerprint"] != fingerprint:
                    raise ShopError("IDEMPOTENCY_CONFLICT", "Key reused for a different order", 409)
                connection.commit()
                return dict(existing)
            subtotal = 0
            for sku, quantity in sorted(quantities.items()):
                product = connection.execute(
                    "SELECT * FROM products WHERE sku = ?", (sku,)
                ).fetchone()
                if product is None:
                    raise ShopError("UNKNOWN_SKU", "Unknown SKU: " + sku, 404)
                if product["stock"] < quantity:
                    raise ShopError("OUT_OF_STOCK", "Insufficient stock: " + sku, 409)
                connection.execute(
                    "UPDATE products SET stock = stock - ? WHERE sku = ?", (quantity, sku)
                )
                subtotal += product["price_cents"] * quantity
            total = discounted_total(subtotal, discount_percent)
            created_at = normalized_time(self.clock().isoformat())
            cursor = connection.execute(
                "INSERT INTO orders(customer_id, request_key, fingerprint, total_cents, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (customer_id, request_key, fingerprint, total, created_at),
            )
            order_id = cursor.lastrowid
            connection.executemany(
                "INSERT INTO order_items VALUES (?, ?, ?)",
                [(order_id, sku, quantity) for sku, quantity in sorted(quantities.items())],
            )
            order = dict(connection.execute(
                "SELECT * FROM orders WHERE id = ?", (order_id,)
            ).fetchone())
            connection.commit()
            return order
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def list_orders(self, customer_id, after_id=0, limit=20):
        required_text(customer_id, "customer_id")
        if type(after_id) is not int or after_id < 0:
            raise ShopError("INVALID_INPUT", "after_id must be a non-negative integer")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ShopError("INVALID_INPUT", "limit must be 1..100")
        connection = connect(self.db_path)
        try:
            rows = connection.execute(
                "SELECT * FROM orders WHERE customer_id = ? AND id > ? ORDER BY id LIMIT ?",
                (customer_id, after_id, limit + 1),
            ).fetchall()
            page = [dict(row) for row in rows[:limit]]
            return {"orders": page, "next_cursor": page[-1]["id"] if len(rows) > limit else None}
        finally:
            connection.close()

    def orders_between(self, customer_id, start, end):
        required_text(customer_id, "customer_id")
        start_utc, end_utc = normalized_time(start), normalized_time(end)
        if start_utc >= end_utc:
            raise ShopError("INVALID_TIME", "start must be earlier than end")
        connection = connect(self.db_path)
        try:
            return [dict(row) for row in connection.execute(
                "SELECT * FROM orders WHERE customer_id = ? AND created_at >= ? "
                "AND created_at < ? ORDER BY created_at, id", (customer_id, start_utc, end_utc)
            )]
        finally:
            connection.close()
