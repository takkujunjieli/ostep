# OrderFlow Instructor Solutions

Read after the attempt. The correct implementation is in the root `shop/` directory. Compare with `diff -u challenge/shop/service.py shop/service.py`; explain the reproduction and cause rather than treating a reference copy as a completed repair.

| Case | Cause | Minimal repair | Discriminating evidence |
|---|---|---|---|
| 01 | Equality is treated as insufficient stock | Change stock <= quantity to stock < quantity | Buy 10 of stock 10 successfully; reject 11 |
| 02 | Retry lookup ignores customer scope | Match both customer_id and request_key | Two customers with the same key receive different orders; same-customer retry deducts once |
| 03 | int(amount) truncates fractions | Use Decimal quantize with ROUND_HALF_UP | 101 at 50 percent yields 51; 303 yields 152 |
| 04 | replace(tzinfo=UTC) relabels instead of converting | Use astimezone(timezone.utc) | UTC, -04:00, and cross-day +14:00 filters agree |
| 05 | id >= after_id repeats the last row | Use id > after_id; preserve ordering and lookahead | Five orders paged by two appear exactly once and terminate |
| 06 | Exception handler commits partial work | Roll back and re-raise | A later item failure restores earlier inventory updates and leaves no order |

Idempotency requires customer scope, a request fingerprint, and concurrency protection. The SQLite unique constraint and BEGIN IMMEDIATE serialize writers before retry and inventory checks. This local technique is not a universal distributed-service design.

Apply the stated money contract: round once after discounting the entire subtotal. Real tax, allocation, or refund systems may have different contracts.

## Optional teaching rubric: 100 points

- Reproduction and diagnosis: 20.
- Correct repair and preserved contracts: 40.
- Regression evidence and adjacent boundaries: 25.
- AI collaboration and explanation: 15.

These are not Amazon hidden tests or official score weights.

## Follow-up questions

1. How do replace(tzinfo=...) and astimezone(...) differ?
2. Why would changing only an inventory message leave the root cause unresolved?
3. How can a client retry safely after a timeout?
4. Why reject a reused key with a different cart?
5. When is checking stock before updating insufficient under concurrency?
6. Why does a correct first page not prove pagination is correct?
7. How can you prove a failed operation leaves no partial writes?

## Further exercises

Cache invalidation, duplicate asynchronous side effects, incorrect filtered counts, and missing authorization are possible extensions. Define the contract and a failing test before introducing a fault.
