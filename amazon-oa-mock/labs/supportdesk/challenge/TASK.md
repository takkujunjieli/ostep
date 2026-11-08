# SupportDesk: Tickets and Replies: Candidate Task

You have inherited an existing Django application. Fix the user reports below. Start the application, read its failures and contract, and trace URL -> view -> service -> repository/model. Preserve the existing API and make a focused fix with regression evidence.

Provenance and limits: Ticket creation and reply failures resemble a candidate account of a Django OA. Thread filtering, close-state persistence, and search are original extensions. The URLs, fields, source code, and specific root causes are locally designed.

## User reports

### Ticket 01: New tickets report success but are missing from the list

Submitting a title and description returns 201, but the new ticket is absent after refreshing. Persist it in the database and set the logged-in user as its owner.

### Ticket 02: The reply endpoint always returns 404

The page submits body to POST /api/tickets/<id>/replies/, but an existing open ticket still returns 404. Trace the request from the URL configuration through the view and service.

### Ticket 03: Support-agent replies disappear from the thread

Customer replies are visible, but replies written by the admin support agent are missing. Show all replies for the ticket, ordered by creation time and then ID.

### Ticket 04: Closed tickets become open again after refreshing

The close endpoint returns closed, but a new read still returns open. Persist the closed status. Closed tickets must reject new replies.

### Ticket 05: Keyword search does not find matching titles

The title Invoice download fails is not found when searching for INVOICE. Trim surrounding query whitespace and use case-insensitive substring matching without exposing another customer private tickets.

## Environment and startup

Python 3.10+, Django 5.2, and SQLite. Dependencies are installed in the repository-root `.venv`. From a bundled `labs/<project>/challenge` directory:

```bash
../../../.venv/bin/python manage.py migrate --run-syncdb
../../../.venv/bin/python seed.py
../../../.venv/bin/python manage.py test app.tests -v 2
../../../.venv/bin/python manage.py runserver 127.0.0.1:8012 --noreload
```

Open http://127.0.0.1:8012/. Demo accounts: alice, bob, admin. Password: `DemoPass123!`. The admin account has staff permissions. Use separate browser sessions when testing multiple users.

For a workspace generated under `runs/`, activate the environment at the repository root with `source .venv/bin/activate` first, then use `python manage.py ...` inside the workspace. The relative interpreter path above is specific to the bundled challenge directories. On a new machine, create a Python 3.12 virtual environment and install `requirements.txt`.

The page sends API requests, refreshes persisted state, and displays the HTTP status and response. All injected faults are in the backend. Interactive data is stored in this directory's `db.sqlite3`; automated tests use a temporary test database.

`seed.py` creates demo records without resetting existing balances, follows, or tickets. Create a fresh workspace to start over.

## Business contract

- Regular users can access only their own tickets; staff can view, reply to, and close any ticket.
- Creating a ticket accepts title and description, trims whitespace, rejects blank input with 400, and returns 201 on success.
- Replies accept body and are permitted only for open tickets. Otherwise return 409 TICKET_CLOSED.
- Both inaccessible and nonexistent tickets return 404.
- Include customer and support-agent replies, ordered by created_at and then id ascending.
- Search within the visible ticket scope, using case-insensitive substring matching on title.

API: GET /api/state/; GET/POST /api/tickets/; GET /api/tickets/<id>/; POST /api/tickets/<id>/replies/; POST /api/tickets/<id>/close/. Search with GET /api/tickets/?q=invoice.

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
