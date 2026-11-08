# MovieDB Instructor Solutions

Read after the attempt. Tickets 01-04 resemble a public candidate comment; ticket 05 is an original extension. All source code and concrete local changes are designed for this exercise.

| Case | Cause and repair | Evidence |
|---|---|---|
| 01 | repository.persist_follow constructs a Follow without save(); persist it before returning | The returned relation has an ID and survives a fresh query |
| 02 | follow_actor returns an existing relation and the view reports 201; restore 400 ALREADY_FOLLOWING | Repeating an existing follow returns 400 without adding a row |
| 03 | unfollow_actor validates but never calls delete() | Delete only the acting user relationship; a second unfollow returns 404 |
| 04 | release_movie sets the cast but never invokes notify_followers | Relevant users receive one notification each; multiple actors and repeated delivery do not duplicate it |
| 05 | mark_read changes memory without saving is_read | Reload remains read, the count falls, and repeated reads are harmless |

Trace app/urls.py -> views -> services -> repository/models. Notifications have a separate notifications.py module.

Acceptance tests directly create some prerequisites so later cases can fail independently of earlier defects. Also test the complete workflow through the page.

Notifications are local database records, not external messages. Do not infer a production-scale architecture from this SQLite exercise.

Grade from the repository root: `python lab.py grade labs/moviedb/challenge`. The correct reference passes all ten tests.
