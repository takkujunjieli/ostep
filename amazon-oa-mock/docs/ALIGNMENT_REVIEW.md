# Alignment Review: Actual Amazon AI Coding OA

Reviewed: 2026-10-24.

**Conclusion: relevant skills, partly supported business scenarios, but not a complete reproduction of an actual OA.** Prioritize MovieDB, then SupportDesk. Wallet and OrderFlow are general debugging supplements. No credible reconstruction percentage can be assigned.

## Evidence and corrections

1. [Amazon officially describes AI-assisted assessments](https://www.aboutamazon.com/news/workplace/artificial-intelligence-resume-jobs-hiring-amazon): candidates use an interactive assistant on a coding platform. The initial search missed this article when looking only at Amazon Jobs preparation pages. Official recognition does not reveal a question bank, fixed bugs, or score weights.
2. [HackerRank documents Guarded and Unguarded modes](https://candidatesupport.hackerrank.com/articles/7634558376-ai-assistant-in-tests), configured by the hiring company. Guarded assistance can include explanations, navigation, and appropriate syntax help; Unguarded offers stronger editing capabilities. Single-file access and a ban on all code suggestions are not universal rules. The page FAQ and mode details have some wording tension, so follow the actual onboarding rather than infer an Amazon setting.
3. [The MovieDB thread](https://www.reddit.com/r/leetcode/comments/1t6luym/amazon_oa_list/) contains separate accounts: the original poster reports follow/unfollow/notification problems and 2/6; commenter Quiet_Preference440 supplies the detailed Spring Boot repair description and 6/6. The previous source attribution conflated them and has been corrected. Neither account is independently verified.
4. [The SupportDesk account](https://leetcode.com/discuss/post/8523471/) names Django, failed creation, failed replies, and six tests. It does not disclose exact models, routes, or causes. A missing save() or singular/plural route mismatch is a local design, not an established actual cause.

## Ticket-level comparison

A reported similar behavior does not establish matching source code, acceptance tests, or difficulty.

| Local ticket | Evidence | Local additions |
|---|---|---|
| MovieDB 01: follow persistence | A commenter explicitly mentions a missing database save | Django implementation and concrete API structure |
| MovieDB 02: duplicate follow | Duplicate validation and 400 are reported | The exact initial erroneous return branch |
| MovieDB 03: unfollow | Validation, 404, and deleting the relation are reported | The local validation already exists; only deletion is removed, narrowing the task |
| MovieDB 04: release notification | A missing service invocation after movie creation is reported | Cast deduplication, delivery idempotency, and transaction checks are practice extensions |
| MovieDB 05: read persistence | Not confirmed by the selected firsthand account | Original extension |
| SupportDesk 01: creation | Failure of that feature is reported | Missing save() is an original cause |
| SupportDesk 02: reply | Failure of that feature is reported | The reply/replies route mismatch is original |
| SupportDesk 03: agent replies | No specific firsthand confirmation | Original extension |
| SupportDesk 04: closing | No specific firsthand confirmation | Original extension |
| SupportDesk 05: search | Not reported for this support-ticket assessment | Original extension |
| Wallet 01: routing | Only secondhand mentions of wallet-style tasks | Original concrete ticket |
| Wallet 02: recipient credit | Unconfirmed | Original concrete ticket |
| Wallet 03: incoming history | Unconfirmed | Original concrete ticket |
| Wallet 04: exact balance | Unconfirmed | Original concrete ticket |
| Wallet 05: rollback | Unconfirmed | Original concrete ticket |

Among fifteen tickets, four have similar concrete behavior reported, two have only symptom-level support, and nine are extensions without comparable evidence. These are source-coverage counts, not probabilities, official weights, or similarity scores.

## Format differences

| Dimension | Evidence | Local difference |
|---|---|---|
| Core work | Amazon confirms AI collaboration; the platform supports repairs and feature completion | Relevant multi-file tracing, API, persistence, and focused edits; the labs are smaller and more explicit |
| Stack | Platform support includes Django, Spring Boot, React/Node and others | All three labs use Django, so they do not exercise Spring injection, Java repositories, or React/Angular wiring |
| Preview | Some accounts describe frontend/backend previews | The local Django-template/JS page mainly displays JSON state; it is not an equivalent React/Angular application |
| Timing | [One candidate](https://leetcode.com/discuss/post/8446202/sde-1-intern-amazon-university-talent-ac-h7t6/) reports 60 minutes | A plausible practice duration, not a universal rule |
| Tickets and tests | That account and SupportDesk report six tests | Five tickets follow the user practice request; ten local checks are instructor-designed. Reports, tests, and independent bugs are different counts |
| Initial failures | Accounts describe reading failures and sometimes incomplete coverage | Local basic tests intentionally pass. Run lab.py grade at the start for exam-style failure-driven practice |
| Assistant | Company-configured capabilities | A single-file/no-patch restriction is an optional stricter exercise; no platform assistant or interaction logging is implemented locally |
| Scoring | Platform interactions can be shown to evaluators; full Amazon weights are unpublished | The 20/40/25/15 rubric is educational. Do not claim official prompt-count or prompt-quality weights |
| Engineering depth | Accounts focus on existing functions and database calls | Concurrency, complex idempotency, and failure injection are supplements, not established mandatory topics |

Platform references: [Code Repository Questions](https://support.hackerrank.com/articles/1900882930-code-repository-questions) and [Code Repos in Tests](https://www.hackerrank.com/release/oct-2025). These describe platform support, not a specific Amazon configuration.

## Recommended preparation

1. Prioritize failing test -> route and call chain -> database read/write -> missing logic -> rerun acceptance. Practice completing an existing feature as well as correcting an expression.
2. Start with MovieDB 01-04 in your strongest framework. If the actual selection is Java, Django practice does not replace Spring-specific preparation.
3. Use SupportDesk 01-02 for the ticket workflow; treat the rest, Wallet, and OrderFlow as supplemental coverage rather than predictions.
4. From the repository root, run `python lab.py grade labs/moviedb/challenge` at the beginning, record failures, and rerun after focused changes. You need not read the grader source to inspect failure output.
5. Verify the full workflow through the page and reload persisted state. Local green tests do not guarantee a recruiting outcome.

The review corrected documentation and source attribution without overwriting challenge business code, databases, or practice changes. Actual alignment still depends on the invitation, official sample, and instructions for the individual assessment.
