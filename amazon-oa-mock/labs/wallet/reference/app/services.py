from contextlib import nullcontext
from django.db import transaction
from django.db.models import F

from core import Problem, positive_int, text
from .models import Transfer, Wallet
from .repository import wallet_for_user


def transfer_money(user, recipient_name, amount_cents, memo=""):
    amount = positive_int(amount_cents)
    recipient_name = text(recipient_name, 150)
    if not isinstance(memo, str) or len(memo) > 160:
        raise Problem("INVALID_INPUT")
    with transaction.atomic():
        sender = wallet_for_user(user)
        recipient = Wallet.objects.filter(user__username=recipient_name).first()
        if recipient is None:
            raise Problem("RECIPIENT_NOT_FOUND", 404)
        if sender.pk == recipient.pk:
            raise Problem("SELF_TRANSFER", 400)
        if sender.balance_cents < amount:
            raise Problem("INSUFFICIENT_FUNDS", 409)
        # Conditional debit prevents a lost update from spending stale funds.
        updated = Wallet.objects.filter(pk=sender.pk, balance_cents__gte=amount).update(balance_cents=F("balance_cents") - amount)
        if not updated:
            raise Problem("INSUFFICIENT_FUNDS", 409)
        Wallet.objects.filter(pk=recipient.pk).update(balance_cents=F("balance_cents") + amount)
        transfer = Transfer.objects.create(sender=sender, recipient=recipient, amount_cents=amount, memo=memo)
        return transfer
