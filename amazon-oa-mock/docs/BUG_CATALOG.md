# Amazon-Style AI Repository Debugging: Bug Catalog

## A. Request routing and API wiring

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| A1 | Path spelling, singular/plural, or slash mismatch produces route 404 | Client URL, root/app URL registration, resolver | Resolve the documented path and POST through it; distinguish HTML route errors from business JSON |
| A2 | Wrong HTTP method or missing method branch | GET/POST/PUT/DELETE dispatch and decorators | Exercise the specified method, then one unsupported method |
| A3 | Wrong route prefix or path converter prevents handler entry | Mounted prefixes and captured parameters | Inspect the resolved function and kwargs for a concrete URL |
| A4 | Parameter name or nesting differs across client and server | Query string, JSON body, path ID, parser | Submit the documented payload and inspect the exact parsed value; include a missing field |
| A5 | Incorrect response status or envelope violates the API contract despite plausible UI behavior | Handler return paths and serializer | Assert status, content type, error code, and required fields rather than status alone |

## B. Persistence and CRUD

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| B1 | Constructed instance is returned without insertion; success with null ID | Model constructor, create/save, caller | Query by returned ID and reread through a separate request |
| B2 | Field assignment changes memory but not the stored row | Mutation, save/update, transaction | Reload from DB and fetch state independently |
| B3 | Unfollow/delete validates existence but never removes the relation | Delete branch and target entity | Assert relation absent, parent entity intact, other users unaffected |
| B4 | Parent exists but collection or many-to-many membership is absent | Membership table, collection update, owning relation side | Add then reread the collection; inspect membership independently |
| B5 | Wrong record is updated or a stale object is serialized | IDs, user/resource mapping, fresh reload | Compare target and control rows plus returned and persisted state |

## C. Query semantics and relationships

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| C1 | Extra author/owner predicate hides valid related records | Thread/collection query and prior authorization | Include multiple authors within one authorized resource and another resource as a control |
| C2 | AND used instead of OR excludes one legitimate role | Query predicates for sender/recipient or similar roles | Test both roles and an unrelated user |
| C3 | Incorrect foreign key, join, relation side, or reverse name | Model relationships and join predicates | Use distinct resource/user IDs; ensure results attach to the intended parent |
| C4 | Join fan-out yields duplicate users or records | Multi-related joins and distinct keys | One user matching two relations should appear only as often as the contract permits |
| C5 | Serializer omits or misnames fields, returns the wrong nesting, or mishandles null | Response projection and frontend consumption | Assert the complete response shape with empty/nonempty data |

## D. Search, sorting, and pagination

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| D1 | Whole-field equality is used when substring or case-insensitive matching is required | ORM lookup or search predicate | Full-title control plus partial and mixed-case queries |
| D2 | Whitespace or other task-required normalization is missing | Query normalization and stated rules | Padded query, blank query, and ordinary query |
| D3 | Numeric values sort as strings, direction is wrong, or tie ordering is unstable | Field types, order direction, secondary key | Values such as 2 and 10; equal timestamps with different IDs |
| D4 | Inclusive cursor or offset boundary repeats/skips records | Cursor predicate, page size, lookahead | Walk several pages; assert no duplicates/omissions and termination |
| D5 | Filtering is applied after pagination, or total/count uses another scope | Filter/order/page sequence and count query | Matching rows across page boundaries; compare count with filtered results |

## E. Inputs and boundary conditions

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| E1 | Missing/null/blank inputs crash or bypass validation | Parsing and validation before side effects | Omitted field, null, whitespace, normal value |
| E2 | Truthiness confuses a valid zero/false with absence, or defaults accept invalid input | if value, defaulting, optional-field contract | Separate missing, zero, false, and an ordinary value |
| E3 | Wrong type is accepted or compared incorrectly | JSON types and conversion | Integer versus string, float, bool, array, object |
| E4 | < versus <=, count-before-increment, or a similar boundary is wrong | Threshold/balance/stock predicate | N-1, N, N+1 around the stated boundary |
| E5 | Empty lists, repeated items, or aggregate quantities are mishandled | List parsing, deduplication, accumulation | Empty list, duplicate SKU/member, aggregate exceeding a limit |

## F. Identity, permissions, and state rules

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| F1 | Client-supplied owner/sender/author overrides authenticated identity | Handler arguments and model assignment | Authenticate as Alice while supplying Bob's identity; verify actual owner/sender |
| F2 | Missing ownership/tenant scope exposes another user's resources | Base queryset and detail lookup | Two users with matching data, plus staff where permitted |
| F3 | Role predicate or authentication middleware is missing/reversed | Login wrapper, staff checks, middleware registration | Anonymous, ordinary user, owner, unrelated user, staff |
| F4 | Forbidden state transition or action after closure/blocking remains allowed | State guard and persisted transition | Trigger the transition through its endpoint, then attempt the next action |
| F5 | Duplicate operation silently succeeds when contract requires rejection, or vice versa | Exists/get/create branches and error contract | First action, repeat action, unchanged row count, different user |

## G. Moderation, counters, and throttling

These behavior categories are reported, but the possible implementation mistakes below are investigation hypotheses rather than a verified source-code reconstruction.

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| G1 | Create is moderated but update bypasses the checker, or neither invokes it | Both write routes, shared utilities/middleware | Same prohibited input through create and update; stored content unchanged on rejection |
| G2 | Violation counter is not saved, is attached to the wrong identity, or resets per request | Counter storage, user key, update operation | Violations across independent requests; reread stored counter |
| G3 | Cumulative/consecutive semantics, threshold, or permanent-block behavior is wrong | Stated rule, increment/reset order, block flag | N-1/N/N+1; interleaved valid/invalid operations according to the actual contract |
| G4 | Rate limits are separate when create/update should share one budget, or different users share it | Limiter key, shared state, route registration | Alternate operations; compare the same user with another user |
| G5 | Checks occur after saving, short-circuit in the wrong order, or keep allowing already blocked users | Middleware/service order and early returns | Rejected operation leaves content unchanged; later request observes the required block state |

## H. Money, atomic operations, and retries

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| H1 | Debit succeeds but credit or ledger creation is omitted | Complete operation and all affected rows | Before/after balances, conserved total, ledger identity |
| H2 | Cents versus dollars, float arithmetic, truncation, or rounding-at-the-wrong-stage changes totals | Units and explicit rounding contract | Half-cent boundary, multi-item subtotal, zero/full discount |
| H3 | Balance check uses wrong account/amount or omits a required self/recipient check | Validation before mutation | Exact balance, insufficient balance, self, unknown recipient |
| H4 | Partial writes survive failure because transaction is missing, committed, or error is swallowed | Transaction boundary and exception paths | Inject a later failure and inspect every earlier write |
| H5 | A retry duplicates effects, or an idempotency key has the wrong user/payload scope | Key lookup, fingerprint, uniqueness, write boundary | Same retry, changed payload, another user using the same key |

## I. Time, expiration, and verification flows

These are General extensions unless a local mapping is shown. Specific password-reset and loan summaries found online were not validated to the same firsthand standard in this review.

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| I1 | Timestamp units, naive/aware times, or timezone relabeling changes an instant | Parsing, UTC conversion, seconds/milliseconds | Equivalent offsets and a cross-date interval |
| I2 | Expiration or interval boundary is reversed or off by one | now/issued_at/expires_at comparisons | Just before, exactly at, and just after the contract boundary |
| I3 | Code/token is missing, compared incorrectly, not invalidated, or checked against the wrong user/request | Generation, storage, verification, consumption | Wrong code, correct code, replacement code, reuse, another user |
| I4 | Password/profile change reports success but authentication still uses old data | Framework-supported credential update and persistence | New independent login after reset, using the stated rules |
| I5 | Rate-limit/reset window never expires or expires too early | Clock units, window key, eviction/reset | Controlled clock around the window boundary without real sleeps |

## J. Control flow, async work, and frontend state

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| J1 | Missing await or unhandled async rejection reports success before work completes | Async calls and response timing | Wait for the operation's completion and force its failure |
| J2 | Missing/incorrect return or middleware continuation invokes the wrong path or responds twice | Early exits and middleware flow | Force each branch; assert one response and no later side effect |
| J3 | Existing helper/event is never invoked, or runs before its inputs are saved | Call sites and data dependencies | Helper works alone but public workflow fails; validate operation order |
| J4 | Backend succeeds but frontend retains stale state, mutates shared state, or ignores errors | Network response, state update, rendered value | Compare API/DB state with the UI after success and rejection |
| J5 | Out-of-order search responses or stale cache overwrite newer state | Request identity, async completion order, cache invalidation | Complete an earlier request after a later one and inspect displayed results |

## K. Concurrency, shared state, and resources

These are supplemental engineering practice rather than established mandatory OA topics.

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| K1 | Read-modify-write loses a concurrent balance/count update | Atomic database update and locking strategy | Controlled concurrent operations plus invariant checks |
| K2 | Check-then-create race produces duplicates or overselling | Uniqueness, conditional writes, transaction scope | Two operations target the same remaining item or relationship |
| K3 | Mutable global/class/default state leaks across users or requests | Shared containers and object lifetime | Independent users and repeated test runs |
| K4 | Cache keys omit user/filter identity or updates leave stale entries | Key construction and invalidation | Two users/queries with different results before and after a write |
| K5 | Unclosed sessions/connections/files or thread-unsafe reuse causes later failures | Resource ownership and cleanup | Repeated operations, isolated workers, failure cleanup |

## L. Framework setup, errors, and test execution

| ID | Pattern and symptom | Inspect first | Discriminating verification |
|---|---|---|---|
| L1 | Missing imports, dependency injection, component registration, or dependency wiring prevents startup/calls | First stack trace, imports, framework configuration | Start/check the app and invoke the affected endpoint |
| L2 | Schema, migrations, database settings, fixtures, or framework versions disagree | Documented setup and actual environment | Reproduce from a clean disposable database/environment |
| L3 | Broad exception handling swallows failures or converts every error to success/500 | Raise/catch mapping and transaction handling | Force a known error; verify response code and no partial writes |
| L4 | Tests use the wrong user/state, leak data, or assert only superficial success | Fixtures, authentication, test isolation, assertions | Run alone and together; check persisted state and a negative control |
| L5 | The wrong server/workspace/interpreter or a non-reloaded build hides the edit | Process, port, working directory, --noreload, environment | Confirm which source is running and repeat the exact failing request |


## Symptom-first triage

| Observation | First discriminating check |
|---|---|
| Route 404 | Resolve the exact documented URL; distinguish route failure from business JSON |
| 200/201 but no visible result | Compare response, stored row, and a fresh authorized read |
| Only some records disappear | Check scope, joins, author predicates, AND/OR, and pagination |
| Repetition causes incorrect behavior | Check duplicate policy, persisted counters, and retry semantics |
| Create works but edit fails or bypasses a rule | Compare the complete create/update call paths |
| An action works after it should be blocked | Persist the transition, then test the next request independently |
| Correct response but inconsistent balances/counts | Verify all affected rows and the invariant, not just the payload |
| Basic tests pass but task behavior fails | Add a case that exercises the exact reported action and rereads state |
| Local edit has no effect | Confirm active workspace, port, interpreter, and reload behavior |

Status numbers alone are insufficient. The same 404 can come from routing, an unknown entity, or an inaccessible entity. A 201 can be hardcoded even when no mutation happened. Error codes and duplicate/idempotency semantics must follow the task contract; do not impose a universal 400/409/404 policy.

## Guided-mode prompts to reuse

1. **Locate the failure layer:**
   > Here is the exact request and response. Determine whether the failure is in routing, authentication, validation, business logic, persistence, querying, serialization, or UI state. Separate observed facts from hypotheses. Do not write a patch.
2. **Trace state changes:**
   > Trace this action from the route to the database and back. For each function, list inputs, reads, writes, return values, and exception behavior. Identify the next inspection step.
3. **Learn an unfamiliar operation:**
   > Explain this framework API and a generic syntax example. State whether it reads, constructs, inserts, updates, or deletes, and whether its effect is immediate, deferred, or asynchronous. Do not solve the ticket for me.
4. **Check scope and invariants:**
   > Identify the user/resource scope and invariant that must remain true. What would happen to another user, a repeated request, a boundary input, and a failed operation?
5. **Design evidence before repair:**
   > Describe a test that fails on the reported defect, a fresh-state check, and a negative control. Do not generate the implementation. Explain which superficially plausible assertions would miss the bug.
6. **Review after a focused change:**
   > Here is my diff and actual output. Explain what passed, what the evidence does not establish, and whether the change alters unrelated behavior. Do not assume tests were run or passed.

The actual assistant mode is configured by the hiring company. [HackerRank documents mode-dependent capabilities](https://candidatesupport.hackerrank.com/articles/7634558376-ai-assistant-in-tests); this catalog is a learning aid, not permission to use external tools in an assessment.

## A minimal verification sequence

1. Read the exact contract: method, path, identity, fields, status/error, persistent effect.
2. Reproduce the action with explicit data and record actual versus expected.
3. Identify the first layer whose behavior disagrees with the contract.
4. Verify one plausible cause with code and an observation rather than making speculative edits.
5. Add a discriminating regression test and confirm it fails before repair.
6. Make the smallest coherent change while preserving scope and adjacent rules.
7. Rerun the reproduction and relevant existing checks; inspect a fresh read and a negative case.
8. Explain the cause, edit, evidence, and practical limits.
