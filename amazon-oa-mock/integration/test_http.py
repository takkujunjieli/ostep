import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from shop.api import make_handler
from shop.db import initialize
from shop.service import OrderService


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        path = Path(self.temp.name) / "http.sqlite3"
        initialize(path)
        handler = make_handler(OrderService(path))
        handler.log_message = lambda *args: None
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.url = "http://127.0.0.1:%s" % self.server.server_port

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def request(self, path, data=None, raw=None):
        body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
        request = Request(self.url + path, data=body, headers={"Content-Type": "application/json"})
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def test_end_to_end_create_retry_and_list(self):
        self.assertEqual(self.request("/health"), (200, {"status": "ok"}))
        self.assertEqual(len(self.request("/products")[1]), 3)
        body = {"customer_id": "alice", "request_key": "r1", "items": [{"sku": "BOOK", "quantity": 1}]}
        status, order = self.request("/orders", body)
        self.assertEqual(status, 200)
        self.assertEqual(order["total_cents"], 1299)
        self.assertEqual(self.request("/orders", body), (200, order))
        self.assertEqual(self.request("/orders?customer_id=alice")[1]["orders"], [order])

    def test_invalid_json_is_400(self):
        self.assertEqual(self.request("/orders", raw=b"{broken")[0], 400)
        self.assertEqual(self.request("/orders", raw=b"[]")[0], 400)

    def test_domain_errors_map_to_http(self):
        body = {"customer_id": "alice", "request_key": "r1", "items": [{"sku": "BOOK", "quantity": 11}]}
        self.assertEqual(self.request("/orders", body)[0], 409)
        body["items"][0]["sku"] = "MISSING"
        self.assertEqual(self.request("/orders", body)[0], 404)

    def test_invalid_queries_and_missing_route(self):
        self.assertEqual(self.request("/orders?customer_id=alice&limit=nope")[0], 400)
        self.assertEqual(self.request("/orders?customer_id=alice&start=bad&end=bad")[0], 400)
        self.assertEqual(self.request("/unknown")[0], 404)
