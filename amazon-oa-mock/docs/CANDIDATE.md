# OrderFlow: AI-Assisted Repository Debugging

You have inherited an order service. Investigate the reports below, repair the existing implementation, and add regression coverage. You may collaborate with an AI assistant, but must understand and explain your final changes.

{{TICKETS}}

## Environment and startup

Python 3.9+ with standard-library dependencies only. Run inside this workspace:

```bash
python3 -m unittest discover -s tests -v
python3 -m shop.api --db practice.sqlite3 --port 8000
```

The server binds only to loopback. In another terminal:

```bash
curl http://127.0.0.1:8000/products
curl -X POST http://127.0.0.1:8000/orders -H 'Content-Type: application/json' -d '{"customer_id":"alice","request_key":"req-1","items":[{"sku":"BOOK","quantity":1}],"discount_percent":0}'
curl 'http://127.0.0.1:8000/orders?customer_id=alice&limit=2'
```

SQLite persists inventory and orders across restarts. Use a new `--db` path to restart with fresh data. Tests always use temporary databases.

## Business contract

- Initial products: BOOK, 1299 cents and stock 10; CABLE, 299 cents and stock 20; PEN, 101 cents and stock 100.
- Aggregate duplicate SKUs within a cart. Exact-stock purchases are valid; overselling is not.
- Scope request_key to the customer. Equivalent retries return the original order without deducting stock twice; changed payloads return 409 IDEMPOTENCY_CONFLICT.
- Store money as integer cents. Discount percentages are integers 0..100. Sum first, discount second, and round once with HALF_UP.
- Require timezone-aware timestamps, normalize to UTC, and filter using [start, end).
- Sort orders by ascending ID. Exclude after_id itself from the next page; return next_cursor=null when no next page exists.
- Any item failure rolls back the whole order. Concurrent requests must preserve inventory and retry semantics.

## File map and API

`shop/api.py` handles HTTP; `shop/service.py` contains business logic; `shop/db.py` defines and initializes SQLite; `tests/` contains the basic suite.

Endpoints: GET /health; GET /products; POST /orders; GET /orders?customer_id=...&after_id=0&limit=20; GET /orders?customer_id=...&start=...&end=.... Encode a plus sign in query timestamps as %2B, or use `curl -G --data-urlencode`.

Creation and equivalent retries return 200. Unknown SKUs return 404. Insufficient stock and key conflicts return 409. Invalid inputs return 400.

customer_id is a local simulation parameter, not authentication. Login, payments, and production deployment are outside this service's scope.

## Practice workflow

Suggested duration: 20-30 minutes per ticket or 60 minutes for the combined challenge, split into 10 minutes to inspect and reproduce, 35 to repair, and 15 to validate and explain. These are not official Amazon timings.

1. Run the basic suite to confirm setup. Passing it does not prove the user report is fixed.
2. Reproduce the symptom with a minimal input and record actual versus expected results.
3. Ask the assistant to trace the call chain and propose testable hypotheses; confirm them by running code.
4. Make a focused fix and add a test that fails before the change and passes afterward. Check adjacent behavior.
5. Explain the cause, change, evidence, and remaining limitations.

Example prompts:

> Read TASK.md and trace the request through the repository. Before editing, give a minimal reproduction and two testable hypotheses.

> Here is the reproduction output. Explain the cause, propose a minimal fix, and check retry, boundary, and transaction behavior.

> Add a discriminating regression test, explain why it fails on the original code, and run the relevant suite.

During blind practice, stay inside this workspace. Read the parent reference implementation, grader, and solutions only afterward. They are not genuinely hidden platform tests.
