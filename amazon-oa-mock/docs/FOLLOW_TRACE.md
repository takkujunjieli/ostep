# Tracing the Follow Request Without Reading the Solution

Use the single-ticket workspace `runs/movie-follow-attempt1`.

## Start with observable behavior

Read TASK.md, sign in as alice, follow actor 1, and refresh the data. Record the POST response and the following list. Browser developer tools -> Network can show the request URL, method, and response.

## Follow the write path

1. In app/views.py, find the Follow form and its data-api URL.
2. In templates/dashboard.html, find form[data-api] and callAPI. Explain how the actor ID becomes part of the URL and how fetch sends the request.
3. Match the URL against app/urls.py. Identify the Python view and captured actor_id argument.
4. Read that function in app/views.py. Inspect its decorator, inputs, service call, and response. Follow @endpoint in core.py if authentication or JSON handling is unclear.
5. Locate the called function in app/services.py. Follow its repository calls without reading unrelated release or notification code.
6. Inspect those functions in app/repository.py, then the Actor and Follow models in app/models.py. Distinguish an in-memory object from a persisted database row.

## Follow the read path too

Refreshing invokes loadState() -> GET /api/state/ -> views.state() -> a Follow query. Explain why the POST response and refreshed list can disagree. A successful HTTP status alone is not proof of persistence.

## Useful searches inside this workspace

```bash
rg -n 'data-api|form\[data-api\]|callAPI|fetch|loadState' app/views.py templates/dashboard.html
rg -n 'follow|api/state' app/urls.py app/views.py
rg -n 'follow_actor|persist_follow|actor_by_id' app/services.py app/repository.py
rg -n 'class Actor|class Follow|UniqueConstraint' app/models.py
```

Write a short table of each function's input, action, and output. Then propose a hypothesis, create a regression test, make a focused change, and validate. The tracing guide deliberately does not supply a patch.

Do not read parent reference/, grader/, SOLUTIONS.md, or lab_support/catalog.py during blind practice.
