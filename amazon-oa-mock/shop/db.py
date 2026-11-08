import sqlite3


def connect(path):
    connection = sqlite3.connect(str(path), timeout=10, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(path):
    with connect(path) as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS products (
                sku TEXT PRIMARY KEY,
                price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
                stock INTEGER NOT NULL CHECK(stock >= 0)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                request_key TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                total_cents INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(customer_id, request_key)
            );
            CREATE TABLE IF NOT EXISTS order_items (
                order_id INTEGER NOT NULL REFERENCES orders(id),
                sku TEXT NOT NULL REFERENCES products(sku),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                PRIMARY KEY(order_id, sku)
            );
            INSERT OR IGNORE INTO products VALUES ('BOOK', 1299, 10);
            INSERT OR IGNORE INTO products VALUES ('CABLE', 299, 20);
            INSERT OR IGNORE INTO products VALUES ('PEN', 101, 100);
        """)
    connection.close()
