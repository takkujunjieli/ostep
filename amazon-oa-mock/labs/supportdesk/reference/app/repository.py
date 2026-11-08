from core import Problem
from .models import Reply, Ticket


def visible_tickets(user):
    return Ticket.objects.all() if user.is_staff else Ticket.objects.filter(owner=user)


def ticket_for_user(user, ticket_id):
    ticket = visible_tickets(user).filter(pk=ticket_id).first()
    if ticket is None:
        raise Problem("TICKET_NOT_FOUND", 404)
    return ticket


def replies_for_ticket(ticket):
    return Reply.objects.filter(ticket=ticket).order_by("created_at", "id")
