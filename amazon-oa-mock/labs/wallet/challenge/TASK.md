# Wallet: Transfers and Ledger: Candidate Task

You have inherited an existing Django application. Fix the user reports below. Start the application, read its failures and contract, and trace URL -> view -> service -> repository/model. Preserve the existing API and make a focused fix with regression evidence.

Provenance and limits: Community discussions contain secondhand mentions of wallet-style framework tasks, but reliable firsthand details are unavailable. All five tickets are original exercises in API routing, database updates, and business-rule debugging.

## User reports

### Ticket 01: The transfer button returns 404

The frontend calls the documented POST /api/transfers/ endpoint, but authenticated requests return 404. Repair the API wiring so normal transfers reach the business layer.

### Ticket 02: The sender is debited but the recipient is not credited

Alice sends Bob 250 cents. Alice loses 250 cents, but Bob balance does not increase. Preserve the combined balance and store amounts as integer cents.

### Ticket 03: Incoming transfers are missing from history

The ledger contains an Alice-to-Bob transfer, but Bob cannot see it in history. Include transfers where the current user is either sender or recipient, without exposing unrelated transactions.

### Ticket 04: Transferring the entire balance fails

Alice has 10000 cents. Sending 9999 succeeds, but sending 10000 reports insufficient funds. Allow a zero balance, never a negative balance, and reject amounts above the balance.

### Ticket 05: Balances change even when the ledger write fails

Inject a failure in Transfer.objects.create. The operation fails, but earlier balance changes remain. Debit, credit, and ledger creation must commit as one transaction.

## Environment and startup

Python 3.10+, Django 5.2, and SQLite. Dependencies are installed in the repository-root `.venv`. From a bundled `labs/<project>/challenge` directory:

```bash
../../../.venv/bin/python manage.py migrate --run-syncdb
../../../.venv/bin/python seed.py
../../../.venv/bin/python manage.py test app.tests -v 2
../../../.venv/bin/python manage.py runserver 127.0.0.1:8013 --noreload
```

Open http://127.0.0.1:8013/. Demo accounts: alice, bob, admin. Password: `DemoPass123!`. The admin account has staff permissions. Use separate browser sessions when testing multiple users.

For a workspace generated under `runs/`, activate the environment at the repository root with `source .venv/bin/activate` first, then use `python manage.py ...` inside the workspace. The relative interpreter path above is specific to the bundled challenge directories. On a new machine, create a Python 3.12 virtual environment and install `requirements.txt`.

The page sends API requests, refreshes persisted state, and displays the HTTP status and response. All injected faults are in the backend. Interactive data is stored in this directory's `db.sqlite3`; automated tests use a temporary test database.

`seed.py` creates demo records without resetting existing balances, follows, or tickets. Create a fresh workspace to start over.

## Business contract

- Amounts are integer cents in the range 1..100000000. Reject bool, float, strings, zero, and negative values.
- The login session determines the sender. Select the recipient by username in recipient.
- Reject self-transfers. Unknown recipients return 404; insufficient funds return 409.
- Success returns 201, debits the sender, credits the recipient, and creates one ledger record.
- Balances can be zero but never negative. Preserve their combined total and commit all writes atomically.
- History includes incoming and outgoing transfers with a direction field, excluding unrelated transactions.
- Payment integrations, fees, idempotent retries, and distributed ledgers are outside the exercise scope.

API: GET /api/state/; GET /api/history/; POST /api/transfers/ (recipient, amount_cents, memo). Ticket 5 uses a mock in its acceptance test to reproduce a ledger-write failure; the other tickets can be reproduced through the page.

## File map

- `config/urls.py`: application routes, login, and sessions.
- `app/urls.py`, `app/views.py`: HTTP routing and request handling.
- `app/services.py`: business workflows.
- `app/repository.py`: queries and persistence; `app/models.py`: ORM schema.
- `core.py`: shared JSON parsing, validation, authentication, and error responses.
- `app/tests/`: basic tests with intentional coverage gaps. Preserve the contract when adding tests.

Use `migrate --run-syncdb` to create the practice schema. This is not a migration debugging task.

## Practice workflow

Suggested limits: 60 minutes for a combined challenge, or 15-25 minutes for one ticket. These are practice settings, not universal Amazon timings or question counts.

1. Begin with a user report or failing request. Locate its route and follow only the relevant call chain.
2. Reproduce with the page or Django test client. Record actual versus expected behavior.
3. Change one root cause at a time and add a regression test that fails before the fix.
4. Run the basic tests. For exam-style practice, run `python lab.py grade <workspace-path>` from the repository root at the start to see the failures, then rerun after changes. It runs 10 acceptance tests. The initially passing basic suite is a teaching choice, not a claim about actual OA tests.
5. Each ticket has one primary acceptance test, plus five shared guard tests. A combined challenge initially fails five primary tests; a single-ticket workspace initially fails only its matching primary test.
6. Explain the cause, changed files, and before/after test evidence.

Two AI practice modes are available:

- **Guided mode, recommended first:** ask for explanations, error analysis, syntax hints, and navigation; write the patch yourself. HackerRank Guarded Mode can allow syntax help and navigation across files. Restricting the assistant to a single file is an optional harder exercise, not a universal platform rule. The hiring company configures actual capabilities.
- **Collaborative mode:** allow generated edits, review each change, and verify the result yourself.

Suggested guided-mode prompt:

> I am doing a local mock assessment. Explain code, analyze errors, offer syntax hints, and suggest the next inspection step, but do not complete the patch or solve the whole task for me. Start with TASK.md and trace relevant files inside this workspace as needed. Do not read the parent reference, grader, lab_support/catalog.py, or SOLUTIONS.md.

Five tickets, ten acceptance tests, and the time limits are local practice choices. A candidate report of six tests does not necessarily mean six independent bugs. See the repository-root `docs/ALIGNMENT_REVIEW.md` for the evidence and differences.

References and solutions live outside this directory. They are not platform-hidden tests; blind practice relies on self-discipline.
