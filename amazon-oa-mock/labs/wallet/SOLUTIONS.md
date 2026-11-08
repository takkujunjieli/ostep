# Wallet Instructor Solutions

All five tickets are original supplemental exercises, not claimed actual wallet assessment questions.

| Case | Cause and repair | Evidence |
|---|---|---|
| 01 | Route is /api/transfer/ instead of /api/transfers/ | An authenticated POST to the documented endpoint returns 201 and creates a ledger record |
| 02 | Debit executes but recipient credit is missing | Sender loses 250, recipient gains 250, combined balance is conserved |
| 03 | History filters only sender; include OR recipient | Incoming transfers are visible to the recipient but not unrelated users |
| 04 | balance <= amount rejects an exact-balance transfer; use < | Transfer all funds to reach zero; still reject an excess amount |
| 05 | nullcontext() removes the transaction; restore transaction.atomic() | A ledger-write exception rolls back both balances and creates no transfer |

Ticket 05 uses unittest.mock.patch to inject a ledger-write failure. It does not need a destructive switch in the page. Service-level tests avoid blocking every case on the routing fault.

Conditional debits and F-expression updates avoid spending or overwriting stale balances. This project does not implement payment gateways, idempotency keys, refunds, fees, or distributed transactions.

Grade from the repository root: `python lab.py grade labs/wallet/challenge`.
