from django.contrib.auth.models import User
from .models import Reply, Ticket


def seed():
    for name in ("alice", "bob", "admin"):
        user, _ = User.objects.get_or_create(username=name)
        user.is_staff = name == "admin"
        user.set_password("DemoPass123!")
        user.save()
    ticket, _ = Ticket.objects.get_or_create(owner=User.objects.get(username="alice"), title="Invoice download fails",
                                           defaults={"description": "The PDF button returns an error."})
    Reply.objects.get_or_create(ticket=ticket, author=User.objects.get(username="admin"), body="Please share the request ID.")
