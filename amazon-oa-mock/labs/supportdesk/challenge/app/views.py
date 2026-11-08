from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from core import endpoint
from . import repository, services


def ticket_json(ticket):
    return {"id": ticket.pk, "title": ticket.title, "description": ticket.description, "status": ticket.status,
            "owner_id": ticket.owner_id}


@login_required
def home(request):
    panels = '''<section><h2>Open a ticket</h2><form data-api="/api/tickets/">
    <label>Title</label><input name="title" value="Cannot download invoice" required>
    <label>Description</label><textarea name="description" required>Clicking download returns an error.</textarea><button>Create ticket</button></form>
    <hr><h2>Ticket conversation</h2><form data-api="/api/tickets/{ticket_id}/replies/">
    <label>Ticket ID</label><input name="ticket_id" type="number" min="1" value="1" required>
    <label>Reply</label><textarea name="body" required>Please share the request ID.</textarea><button>Reply</button></form>
    <form data-api="/api/tickets/{ticket_id}/" data-method="GET"><label>Ticket ID</label><input name="ticket_id" type="number" min="1" value="1" required><button>Read thread</button></form>
    <form data-api="/api/tickets/{ticket_id}/close/"><label>Ticket ID</label><input name="ticket_id" type="number" min="1" value="1" required><button>Close ticket</button></form>
    <hr><h2>Search</h2><form data-api="/api/tickets/" data-method="GET"><label>Title contains</label><input name="q" value="invoice"><button>Search</button></form></section>'''
    return render(request, "dashboard.html", {"title": "SupportDesk", "description": "Customers open tickets. The owner and support admin can discuss and resolve them.", "panels": panels})


@endpoint("GET")
def state(request, data):
    tickets = repository.visible_tickets(request.user).order_by("id")
    return JsonResponse({"tickets": [dict(ticket_json(ticket), replies=list(repository.replies_for_ticket(ticket).values("id", "author_id", "body"))) for ticket in tickets]})


def tickets(request):
    if request.method == "GET":
        return list_tickets(request)
    return create(request)


@endpoint("GET")
def list_tickets(request, data):
    return JsonResponse({"tickets": [ticket_json(ticket) for ticket in services.search_tickets(request.user, request.GET.get("q", ""))]})


@endpoint("POST")
def create(request, data):
    ticket = services.create_ticket(request.user, data.get("title"), data.get("description"))
    return JsonResponse(ticket_json(ticket), status=201)


@endpoint("GET")
def detail(request, data, ticket_id):
    ticket = repository.ticket_for_user(request.user, ticket_id)
    return JsonResponse(dict(ticket_json(ticket), replies=list(repository.replies_for_ticket(ticket).values("id", "author_id", "body"))))


@endpoint("POST")
def reply(request, data, ticket_id):
    result = services.reply_to_ticket(request.user, ticket_id, data.get("body"))
    return JsonResponse({"id": result.pk, "ticket_id": ticket_id, "body": result.body}, status=201)


@endpoint("POST")
def close(request, data, ticket_id):
    return JsonResponse(ticket_json(services.close_ticket(request.user, ticket_id)))
