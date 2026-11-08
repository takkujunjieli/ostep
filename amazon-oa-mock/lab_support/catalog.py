"""Instructor catalog. Spoilers: do not read during a blind attempt."""


def ticket(title, report, file, before, after, test):
    return {"title": title, "report": report, "file": file, "before": before, "after": after, "test": test}


CATALOG = {
    "moviedb": {
        "title": "MovieDB: Follows and Notifications",
        "port": 8011,
        "provenance": "Follow persistence, duplicate validation, unfollowing, and release notifications resemble the Spring Boot account posted by commenter Quiet_Preference440. This implementation uses Django. Additional contracts such as notification deduplication and the read-state ticket are original extensions; no actual assessment source code is used.",
        "tickets": [
            ticket("Following appears successful but disappears after refresh", "Alice follows actor 1 and receives a success response, but the following list is still empty after refreshing. The follow relationship must persist in the database.", "repository.py", "    follow.save()", "    # Save is handled by the caller.", "test_01_follow_is_persisted"),
            ticket("Duplicate follows do not return the expected error", "Following the same actor twice as the same user must return 400 ALREADY_FOLLOWING and leave exactly one relationship. The second request currently reports success.", "services.py", '        raise Problem("ALREADY_FOLLOWING", 400)', "        return Follow.objects.get(user=user, actor=actor)", "test_02_duplicate_follow_returns_400"),
            ticket("Unfollowing does not take effect", "An existing relationship remains in the list after unfollowing. Delete only the current user relationship. Return 404 if it does not exist, and preserve other users relationships.", "services.py", "    follow.delete()", "    # Existing relation has been validated.", "test_03_unfollow_deletes_only_own_relation"),
            ticket("New releases do not notify followers", "An admin publishes a movie with a cast list, but followers of its actors receive no notification. Each relevant user should receive exactly one notification per movie; unrelated users should receive none.", "services.py", "    notifications.notify_followers(movie)", "    # Movie and cast have been saved.", "test_04_release_notifies_distinct_followers"),
            ticket("Read status is lost after refreshing", "Marking a notification as read reports success, but refreshing shows it as unread and restores the badge count. Persist the state, make repeated reads safe, and allow changes only to the current user notifications.", "services.py", '    notification.save(update_fields=["is_read"])', "    # The response contains the updated state.", "test_05_read_notification_persists_and_updates_count"),
        ],
        "contract": """- Creating a follow returns 201; duplicate follows return 400. Unfollowing returns 200, or 404 when the relationship does not exist.
- The login session determines the acting user; a supplied user_id cannot change that identity.
- Only staff can publish movies. Save the movie and its cast before notifying followers.
- Each user receives at most one notification per movie, even when following several cast members.
- Marking a notification as read is idempotent and persistent. Count only the current user unread notifications.
- Tests may directly create existing follows or notifications to exercise downstream features independently.

API: GET /api/state/; POST /api/actors/<id>/follow/; POST /api/actors/<id>/unfollow/; POST /api/movies/ (title, cast_ids); POST /api/notifications/<id>/read/.""",
    },
    "supportdesk": {
        "title": "SupportDesk: Tickets and Replies",
        "port": 8012,
        "provenance": "Ticket creation and reply failures resemble a candidate account of a Django OA. Thread filtering, close-state persistence, and search are original extensions. The URLs, fields, source code, and specific root causes are locally designed.",
        "tickets": [
            ticket("New tickets report success but are missing from the list", "Submitting a title and description returns 201, but the new ticket is absent after refreshing. Persist it in the database and set the logged-in user as its owner.", "services.py", "    ticket.save()", "    # Ticket is ready for serialization.", "test_01_new_ticket_is_saved_and_owned"),
            ticket("The reply endpoint always returns 404", "The page submits body to POST /api/tickets/<id>/replies/, but an existing open ticket still returns 404. Trace the request from the URL configuration through the view and service.", "urls.py", 'path("api/tickets/<int:ticket_id>/replies/", views.reply)', 'path("api/tickets/<int:ticket_id>/reply/", views.reply)', "test_02_reply_route_reaches_service"),
            ticket("Support-agent replies disappear from the thread", "Customer replies are visible, but replies written by the admin support agent are missing. Show all replies for the ticket, ordered by creation time and then ID.", "repository.py", "Reply.objects.filter(ticket=ticket).order_by", "Reply.objects.filter(ticket=ticket, author=ticket.owner).order_by", "test_03_thread_includes_support_agent_replies"),
            ticket("Closed tickets become open again after refreshing", "The close endpoint returns closed, but a new read still returns open. Persist the closed status. Closed tickets must reject new replies.", "services.py", '    ticket.save(update_fields=["status"])', "    # Return the updated ticket.", "test_04_closed_status_survives_reload"),
            ticket("Keyword search does not find matching titles", "The title Invoice download fails is not found when searching for INVOICE. Trim surrounding query whitespace and use case-insensitive substring matching without exposing another customer private tickets.", "services.py", "tickets.filter(title__icontains=query.strip())", "tickets.filter(title=query.strip())", "test_05_search_is_partial_and_case_insensitive"),
        ],
        "contract": """- Regular users can access only their own tickets; staff can view, reply to, and close any ticket.
- Creating a ticket accepts title and description, trims whitespace, rejects blank input with 400, and returns 201 on success.
- Replies accept body and are permitted only for open tickets. Otherwise return 409 TICKET_CLOSED.
- Both inaccessible and nonexistent tickets return 404.
- Include customer and support-agent replies, ordered by created_at and then id ascending.
- Search within the visible ticket scope, using case-insensitive substring matching on title.

API: GET /api/state/; GET/POST /api/tickets/; GET /api/tickets/<id>/; POST /api/tickets/<id>/replies/; POST /api/tickets/<id>/close/. Search with GET /api/tickets/?q=invoice.""",
    },
    "wallet": {
        "title": "Wallet: Transfers and Ledger",
        "port": 8013,
        "provenance": "Community discussions contain secondhand mentions of wallet-style framework tasks, but reliable firsthand details are unavailable. All five tickets are original exercises in API routing, database updates, and business-rule debugging.",
        "tickets": [
            ticket("The transfer button returns 404", "The frontend calls the documented POST /api/transfers/ endpoint, but authenticated requests return 404. Repair the API wiring so normal transfers reach the business layer.", "urls.py", 'path("api/transfers/", views.transfer)', 'path("api/transfer/", views.transfer)', "test_01_documented_transfer_route_exists"),
            ticket("The sender is debited but the recipient is not credited", "Alice sends Bob 250 cents. Alice loses 250 cents, but Bob balance does not increase. Preserve the combined balance and store amounts as integer cents.", "services.py", '        Wallet.objects.filter(pk=recipient.pk).update(balance_cents=F("balance_cents") + amount)', "        # Recipient wallet was loaded above.", "test_02_transfer_credits_recipient_and_conserves_total"),
            ticket("Incoming transfers are missing from history", "The ledger contains an Alice-to-Bob transfer, but Bob cannot see it in history. Include transfers where the current user is either sender or recipient, without exposing unrelated transactions.", "repository.py", "Q(sender=wallet) | Q(recipient=wallet)", "Q(sender=wallet)", "test_03_history_includes_incoming_and_excludes_other_users"),
            ticket("Transferring the entire balance fails", "Alice has 10000 cents. Sending 9999 succeeds, but sending 10000 reports insufficient funds. Allow a zero balance, never a negative balance, and reject amounts above the balance.", "services.py", "if sender.balance_cents < amount:", "if sender.balance_cents <= amount:", "test_04_exact_balance_transfer_succeeds"),
            ticket("Balances change even when the ledger write fails", "Inject a failure in Transfer.objects.create. The operation fails, but earlier balance changes remain. Debit, credit, and ledger creation must commit as one transaction.", "services.py", "    with transaction.atomic():", "    with nullcontext():", "test_05_ledger_failure_rolls_back_both_balances"),
        ],
        "contract": """- Amounts are integer cents in the range 1..100000000. Reject bool, float, strings, zero, and negative values.
- The login session determines the sender. Select the recipient by username in recipient.
- Reject self-transfers. Unknown recipients return 404; insufficient funds return 409.
- Success returns 201, debits the sender, credits the recipient, and creates one ledger record.
- Balances can be zero but never negative. Preserve their combined total and commit all writes atomically.
- History includes incoming and outgoing transfers with a direction field, excluding unrelated transactions.
- Payment integrations, fees, idempotent retries, and distributed ledgers are outside the exercise scope.

API: GET /api/state/; GET /api/history/; POST /api/transfers/ (recipient, amount_cents, memo). Ticket 5 uses a mock in its acceptance test to reproduce a ledger-write failure; the other tickets can be reproduced through the page.""",
    },
}
