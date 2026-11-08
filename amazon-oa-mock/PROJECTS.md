# AI Coding Repository Practice Library

For a cross-project review, see [the bug catalog](docs/BUG_CATALOG.md): 60 preparation patterns, evidence labels, symptom-based triage, and Guided-mode prompts. It includes all 21 local tickets plus additional reported scenarios and general extensions.

Three Django 5.2 + SQLite applications provide session login and interactive pages. Trace real framework code from URL to view, service, repository, and ORM. No Amazon source code is included, and the stack, timing, and ticket counts are not guaranteed to match a particular assessment.

**Review conclusion:** the skills are relevant, but the full projects are not actual OA reproductions. Among 15 tickets, four resemble concrete reported behaviors, two match only reported symptoms, and nine are original extensions. These counts describe evidence coverage, not hit rate. See [the alignment review](docs/ALIGNMENT_REVIEW.md).

## Suggested order

| Order | Project | Five tickets | Evidence |
|---|---|---|---|
| 1 | [MovieDB](labs/moviedb/challenge/TASK.md) | Follow persistence, duplicate follow, unfollow, release notifications, read state | The first four resemble a candidate comment; the fifth is an extension |
| 2 | [SupportDesk](labs/supportdesk/challenge/TASK.md) | Ticket persistence, reply route, missing agent replies, close persistence, search | Creation and reply symptoms are reported; exact causes and other tickets are original |
| 3 | [Wallet](labs/wallet/challenge/TASK.md) | Transfer route, recipient credit, incoming history, exact-balance boundary, rollback | Wallet-style tasks have only secondhand mentions; all five concrete tickets are original |
| Optional | [OrderFlow](challenge/TASK.md) | Six original engineering faults | Supplemental business-logic and boundary practice |

The exercises include missing database writes, incorrect route wiring, and existing services that are never invoked. They exercise the repository workflow described in candidate accounts. See [sources](docs/SOURCES.md).

## Start a project

Run from the directory containing this file:

```bash
source .venv/bin/activate
cd labs/moviedb/challenge
python manage.py migrate --run-syncdb
python seed.py
python manage.py test app.tests -v 2
python manage.py runserver 127.0.0.1:8011 --noreload
```

For SupportDesk use `labs/supportdesk/challenge` and port 8012. For Wallet use `labs/wallet/challenge` and port 8013.

Demo users: alice, bob, admin. Password: `DemoPass123!`. The admin account is staff. Separate browser sessions help test customer/admin workflows: follow -> publish -> receive notification, or open ticket -> agent reply -> read thread.

Dependencies are already installed locally. On a new machine, run `python3.12 -m venv .venv`, activate it, and install with `python -m pip install -r lab_support/base/requirements.txt`. The original OrderFlow service does not require Django.

`migrate --run-syncdb` creates the app schema. `seed.py` creates demo records without resetting existing balances, follows, or tickets. Interactive data uses the workspace SQLite file; tests use temporary databases.

## Single-ticket practice

Generate an independent workspace from the repository root:

```bash
source .venv/bin/activate
python lab.py new moviedb --case 01 --dest runs/movie-follow-attempt1
cd runs/movie-follow-attempt1
python manage.py migrate --run-syncdb
python seed.py
python manage.py test app.tests -v 2
python manage.py runserver 127.0.0.1:8011 --noreload
```

Projects: moviedb, supportdesk, wallet. Cases: 01..05. Omit --case to generate a five-ticket combined challenge. Existing destinations are refused; choose a new --dest for another attempt.

Suggested durations: 60 minutes combined, 15-25 minutes per ticket. These are practice settings. Make focused changes rather than rewriting the application.

## Acceptance checks

From the repository root:

```bash
python lab.py grade labs/moviedb/challenge
python lab.py grade labs/supportdesk/challenge
python lab.py grade labs/wallet/challenge
python lab.py grade runs/movie-follow-attempt1
```

Each project has ten acceptance tests: five primary feature checks plus five guards. Initially, a combined challenge should fail five primary tests; an isolated case should fail just its own primary test. A complete repair passes 10/10 with exit code zero. These numbers do not map to official Amazon scores.

Basic tests deliberately leave gaps. Add a discriminating reproduction test and verify persisted state, permissions, invalid input, or failure behavior. Do not weaken tests to avoid a repair.

For exam-style practice, run the grader at the beginning to obtain a failure list, then inspect and iterate. Writing your own tests first is an alternative teaching workflow, not a claim that actual OA failures are hidden until the end. Five reports are not equivalent to a candidate account of six test cases.

## AI modes

**Guided mode:** ask for explanations, errors, call paths, syntax hints, and navigation; write the patch yourself. HackerRank Guarded Mode can allow syntax help and cross-file navigation. Restricting the assistant to one selected file is an optional harder exercise, not a universal rule. Follow the actual test onboarding.

**Collaborative mode:** allow edits, review them, and validate behavior. Explain the reproduction, root cause, minimal repair, and test evidence in either mode. TASK.md includes a reusable prompt.

## References and maintenance

- `labs/<project>/reference/app`: correct app source; read after the attempt.
- `labs/<project>/grader`: instructor acceptance tests.
- `labs/<project>/SOLUTIONS.md`: five-ticket explanations.
- `lab_support/base`: shared scaffold copied into independent workspaces.
- `lab_support/catalog.py`: instructor fault injection and reports; contains spoilers.
- `python lab.py selfcheck all`: verify three references, fifteen isolated cases, and three combined challenges without modifying attempts.
- `python lab.py reference moviedb --dest runs/movie-reference`: create a runnable reference for comparison after practice.

Optional teaching rubric: reproduction 20, correctness 40, regression evidence 25, explanation and AI judgment 15. These are not official weights.

Prioritize MovieDB 01-04, then SupportDesk 01-02. Django practice does not replace Spring-specific preparation if you choose Java. Concurrency and distributed idempotency have not been established as mandatory topics by the reviewed evidence.
