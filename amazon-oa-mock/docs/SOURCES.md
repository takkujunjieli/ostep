# Sources and Scope

Additional review on 2026-10-25: [BUG_CATALOG.md](BUG_CATALOG.md) extends preparation beyond the existing projects while preserving the distinction between reported symptoms, local defects, and general practice. It does not establish a comprehensive real-question bank.

Reviewed: 2026-10-24. Sources support only the claims described below. They do not establish a universal question bank, format, score distribution, or question frequency.

## Amazon preparation pages

1. [Amazon: SDE online assessment preparation](https://amazon.jobs/content/en/how-we-hire/university/sde-oa). Describes coding and technical problem solving; structure can vary by country, so check the invitation.
2. [Amazon: SDE II OA preparation](https://amazon.jobs/content/en/how-we-hire/sde-ii-oa-prep). Describes coding, system design, and work styles, with emphasis on correct and robust implementations.

These pages do not publish a unified 2026 AI repository specification or fixed bug list. Local language choices, scenarios, timing, and scoring are practice designs.

## Candidate accounts and community comments

Accounts are not independently verified official questions. Some entries are firsthand accounts and others secondhand comments. See [the alignment review](ALIGNMENT_REVIEW.md) for ticket-level distinctions.

3. [Reddit: amazon oa list](https://www.reddit.com/r/leetcode/comments/1t6luym/amazon_oa_list/). Attribution correction: the original poster describes MovieDB follow/unfollow/notification problems and reports 2/6. The detailed Spring Boot repairs and 6/6 account come from commenter Quiet_Preference440: persist follows, reject duplicates with 400, validate/delete unfollows, and invoke notifications after publishing. The local first four MovieDB tickets resemble those behaviors but use Django. Read-state persistence and extra deduplication contracts are extensions, not confirmed by that account.
4. [LeetCode: Amazon SDE Intern OA Experience](https://leetcode.com/discuss/post/8523471/). Describes a Django support-ticket app, failed ticket creation and replies, and six tests. Models, routes, root causes, and all local implementation details are original. The other three SupportDesk tickets are extensions.
5. [Reddit: AI-assisted repository preparation discussion](https://www.reddit.com/r/LeetcodeDesi/comments/1vf8vgu/got_an_amazon_sde_online_assessment_with/). Some commenters describe an assistant limited to explanations and navigation. This motivates an optional guided mode, not a universal claim about every test.
6. [Reddit: Amazon OA discussion, September 29](https://www.reddit.com/r/amazonsdeprep/comments/1wtldzc/amazon_oa/). A reply mentions wallet-style tasks and stack choices secondhand. Evidence is weaker than the specific accounts above. All five local Wallet tickets are original supplements.

## Official AI and platform information

7. [Amazon: AI innovations in hiring](https://www.aboutamazon.com/news/workplace/artificial-intelligence-resume-jobs-hiring-amazon). Officially confirms interactive AI assistance on a coding platform, but does not publish detailed questions or uniform scoring weights.
8. [HackerRank: AI Assistant in Tests](https://candidatesupport.hackerrank.com/articles/7634558376-ai-assistant-in-tests). Guarded and Unguarded capabilities are configured by the hiring company. A single-file-only or no-code-at-all rule is not universal. The FAQ wording and mode details are not fully consistent, so do not infer a specific Amazon configuration.
9. [HackerRank: Code Repository Questions](https://support.hackerrank.com/articles/1900882930-code-repository-questions). Supports repository tasks for repairs and feature work. Platform capabilities do not establish a specific Amazon paper.
10. [LeetCode: SDE 1 INTERN OA account](https://leetcode.com/discuss/post/8446202/sde-1-intern-amazon-university-talent-ac-h7t6/). Reports a 60-minute repository task, six tests, and a framework selection that cannot be changed after starting. These describe one account, not global rules; test count is not bug count.

## Additional candidate scenarios reviewed on 2026-10-25

- [Amazon Intern OA, original poster follow-up](https://www.reddit.com/r/leetcode/comments/1vjnfvz/amazon_intern_oa/): the poster describes a movie app that could not add movies to a watchlist. This supports the symptom, not an exact missing-save or relationship implementation.
- [Review moderation and rate limiting](https://www.reddit.com/r/csMajors/comments/1tf9kve/amazon_aiassisted_oa_fullstack_debugging_problem/): a first-person account describes create/update moderation, persisted violation tracking, blocking, and a shared rate limit. Its thresholds are particular reported requirements, not universal rules. Consecutive and cumulative rules must be clarified from the actual task.
- [Movie search comment](https://www.reddit.com/r/leetcode/comments/1t1u0au/amazon_oa_ai_assisted_code_repository/): a commenter describes search defects with Django. This does not confirm the exact original lookup or the locally designed SupportDesk search cause.

Password-reset and loan scenarios found in secondary summaries were not verified to the same standard in this review. They remain general extensions in the catalog. The historical 2026-10-24 alignment report remains a dated assessment of its selected sources.

## Framework references

- [Django supported releases](https://www.djangoproject.com/download/): the labs use the supported 5.2 LTS series, installed and pinned locally at 5.2.18.
- [Django 5.2 installation FAQ](https://docs.djangoproject.com/en/5.2/faq/install/): Python 3.10+. The local environment uses Python 3.12; the original standard-library OrderFlow service remains separate.
