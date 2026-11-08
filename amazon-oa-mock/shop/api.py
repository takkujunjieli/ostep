"""A loopback-only HTTP adapter for the local interview service."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .db import initialize
from .service import OrderService, ShopError


def make_handler(service):
    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, data):
            payload = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            self.dispatch("GET")

        def do_POST(self):
            self.dispatch("POST")

        def dispatch(self, method):
            try:
                url = urlparse(self.path)
                query = parse_qs(url.query)
                if method == "GET" and url.path == "/health":
                    return self.respond(200, {"status": "ok"})
                if method == "GET" and url.path == "/products":
                    return self.respond(200, service.products())
                if method == "GET" and url.path == "/orders":
                    customer = query.get("customer_id", [None])[0]
                    if "start" in query or "end" in query:
                        orders = service.orders_between(customer, query.get("start", [None])[0],
                                                        query.get("end", [None])[0])
                        return self.respond(200, {"orders": orders})
                    return self.respond(200, service.list_orders(
                        customer, int(query.get("after_id", [0])[0]),
                        int(query.get("limit", [20])[0])))
                if method == "POST" and url.path == "/orders":
                    size = int(self.headers.get("Content-Length", "0"))
                    if not 0 < size <= 65536:
                        raise ShopError("INVALID_INPUT", "Body must be 1..65536 bytes")
                    body = json.loads(self.rfile.read(size))
                    if not isinstance(body, dict):
                        raise ShopError("INVALID_INPUT", "Body must be an object")
                    order = service.create_order(body.get("customer_id"), body.get("request_key"),
                                                 body.get("items"), body.get("discount_percent", 0))
                    return self.respond(200, order)
                self.respond(404, {"error": "NOT_FOUND"})
            except ShopError as error:
                self.respond(error.status, {"error": error.code, "message": str(error)})
            except (ValueError, UnicodeDecodeError):
                self.respond(400, {"error": "INVALID_INPUT", "message": "Invalid JSON or query value"})
            except Exception:
                self.log_error("Unhandled request error")
                self.respond(500, {"error": "INTERNAL_ERROR"})

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="shop.sqlite3")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    initialize(args.db)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(OrderService(args.db)))
    print("Order API: http://127.0.0.1:%s (Ctrl-C to stop)" % server.server_port, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
