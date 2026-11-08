from django.db.models import Q
from core import Problem
from .models import Transfer, Wallet


def wallet_for_user(user):
    wallet = Wallet.objects.filter(user=user).first()
    if wallet is None:
        raise Problem("WALLET_NOT_FOUND", 404)
    return wallet


def history_for_wallet(wallet):
    return Transfer.objects.filter(Q(sender=wallet) | Q(recipient=wallet)).order_by("id")
