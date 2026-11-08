# Amazon OA AI Coding: Local Mock Projects (2026)

Original repository-debugging practice, not leaked questions or official Amazon assessment content. Practice understanding an unfamiliar repository, reproducing a user report, working with an AI assistant, making a focused repair, and proving the result.

Cross-project reference: [Bug Catalog](docs/BUG_CATALOG.md), reviewed 2026-10-25, covers 60 debugging patterns, evidence levels, the 21 local tickets, symptom-based diagnosis, and reusable Guided-mode prompts.

## Django project library

Three runnable projects provide **15 tickets**: MovieDB, SupportDesk, and Wallet. Each has a five-ticket combined challenge, independently generated single-ticket workspaces, Django ORM with SQLite, session login, an interactive page, three basic tests, and ten acceptance tests.

Start with [PROJECTS.md](PROJECTS.md). MovieDB and SupportDesk draw on specific candidate accounts; Wallet is supplemental original practice. The implementation, stack versions, and extra contracts are locally designed.

The [alignment review](docs/ALIGNMENT_REVIEW.md) distinguishes reported behavior, reported symptoms, and original extensions. Skills are aligned, but the full projects are not equivalent reproductions of actual assessments.

Django dependencies are installed in `.venv` and require Python 3.10+; Python 3.12 is recommended. From this directory:

```bash
source .venv/bin/activate
cd labs/moviedb/challenge
python manage.py migrate --run-syncdb
python seed.py
python manage.py runserver 127.0.0.1:8011 --noreload
```

Open http://127.0.0.1:8011/. Demo users: alice, bob, admin. Password: `DemoPass123!`. Each TASK.md includes guided and collaborative AI practice modes.

## Original OrderFlow project

The original Python + SQLite order backend uses only the standard library and supports Python 3.9+. It includes HTTP endpoints, persistent inventory, discounts, customer-scoped idempotency, pagination, and time filtering.

Begin the six-ticket combined challenge:

```bash
cd challenge
cat TASK.md
python3 -m unittest discover -s tests -v
python3 -m shop.api --db practice.sqlite3 --port 8000
```

Generate one isolated fault from the repository root:

```bash
python3 manage.py new 01
cd runs/01
cat TASK.md
python3 -m unittest discover -s tests -v
```

Choose 01..06 or all. Existing destinations are never overwritten. Use a new destination for another attempt: `python3 manage.py new 01 --dest runs/01-attempt2`.

Grade from the repository root:

```bash
python3 manage.py grade challenge
# Or: python3 manage.py grade runs/01
```

The grader runs 25 regression tests and exits with zero when all pass. An unfixed challenge is expected to fail. The four basic tests deliberately leave gaps so that user reports require new reproduction tests.

| Case | Symptom | Focus |
|---|---|---|
| 01 | Exact-stock purchases fail | Boundary conditions |
| 02 | Different customers receive the same order | Idempotency scope and data isolation |
| 03 | Discounts lose a cent | Money rounding and business contracts |
| 04 | Offset-aware searches miss orders | Timezone conversion and cross-day intervals |
| 05 | Pagination repeats orders | Exclusive cursor boundaries |
| 06 | Failed orders reduce inventory | Atomic rollback and failure paths |

These are original fault designs, not a claim about actual Amazon questions or their frequency. Regression coverage also checks concurrent retries, purchases, validation, persistence, and duplicate SKU aggregation.

## Repository map

```text
PROJECTS.md          Django project guide
lab.py               Django workspace generation, grading, and self-checks
labs/                Django challenges, reference app code, graders, solutions
lab_support/         Shared Django scaffold, task template, instructor catalog
challenge/           Original OrderFlow candidate challenge
shop/                Correct OrderFlow reference implementation
 tests/              OrderFlow basic tests
 grader/             OrderFlow instructor acceptance tests
 docs/               Candidate template, solutions, sources, alignment review
manage.py            OrderFlow workspace generation and grading
```

The reference backend can run with `python3 -m shop.api --db reference.sqlite3`. Its customer_id parameter simulates a user; it has no authentication or payment integration.

## Maintainer verification

```bash
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s grader -v
python3 -m unittest discover -s integration -v
python3 manage.py selfcheck
.venv/bin/python lab.py selfcheck all
```

Self-checks use temporary data. They verify clean references and assert that each intentionally broken variant fails only its designated acceptance checks. They do not modify existing attempts. HTTP integration tests require permission to bind to a loopback port.
