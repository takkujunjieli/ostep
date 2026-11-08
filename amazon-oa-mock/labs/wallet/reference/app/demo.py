from django.contrib.auth.models import User
from .models import Wallet


def seed():
    for name in ("alice", "bob", "admin"):
        user, _ = User.objects.get_or_create(username=name)
        user.is_staff = name == "admin"
        user.set_password("DemoPass123!")
        user.save()
        Wallet.objects.get_or_create(user=user, defaults={"balance_cents": 10000})
