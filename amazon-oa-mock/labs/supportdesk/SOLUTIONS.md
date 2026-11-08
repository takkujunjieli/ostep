# SupportDesk Instructor Solutions

Creation and reply symptoms draw on a candidate account of a Django assessment. Exact root causes are original; the remaining three tickets are extensions.

| Case | Cause and repair | Evidence |
|---|---|---|
| 01 | create_ticket never calls ticket.save() | The 201 response contains a non-null ID and the owner-scoped record exists |
| 02 | app/urls.py uses /reply/ while the documented client calls /replies/ | The documented route reaches the view and creates a Reply |
| 03 | replies_for_ticket filters by author=ticket.owner and excludes agents | Include every author for that ticket, ordered by creation time and ID |
| 04 | close_ticket changes only memory; persist status | A new query remains closed and the service rejects subsequent replies |
| 05 | Search uses exact title equality; use title__icontains with a trimmed query | Partial case-insensitive matches work without exposing another user tickets |

Preserve authorization. Do not make everyone staff or change the client contract just to hide a backend mismatch.

Grade from the repository root: `python lab.py grade labs/supportdesk/challenge`.
