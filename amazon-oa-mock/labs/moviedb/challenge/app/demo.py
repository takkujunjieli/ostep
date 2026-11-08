from django.contrib.auth.models import User
from .models import Actor, Movie


def seed():
    for name in ("alice", "bob", "admin"):
        user, _ = User.objects.get_or_create(username=name)
        user.is_staff = name == "admin"
        user.set_password("DemoPass123!")
        user.save()
    for name in ("Maya Chen", "Alex Rivera", "Sam Morgan"):
        Actor.objects.get_or_create(name=name)
    Movie.objects.get_or_create(title="The First Frame")
