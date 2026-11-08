from core import Problem, text
from . import repository
from .models import Reply, Ticket


def create_ticket(user, title, description):
    ticket = Ticket(owner=user, title=text(title, 160), description=text(description, 5000))
    ticket.save()
    return ticket


def reply_to_ticket(user, ticket_id, body):
    ticket = repository.ticket_for_user(user, ticket_id)
    if ticket.status != "open":
        raise Problem("TICKET_CLOSED", 409)
    return Reply.objects.create(ticket=ticket, author=user, body=text(body, 5000))


def close_ticket(user, ticket_id):
    ticket = repository.ticket_for_user(user, ticket_id)
    ticket.status = "closed"
    ticket.save(update_fields=["status"])
    return ticket


def search_tickets(user, query):
    tickets = repository.visible_tickets(user)
    if query.strip():
        tickets = tickets.filter(title__icontains=query.strip())
    return tickets.order_by("id")
