from django.conf import settings
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance_cents = models.BigIntegerField(default=0)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(balance_cents__gte=0), name="nonnegative_balance")]


class Transfer(models.Model):
    sender = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="sent")
    recipient = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="received")
    amount_cents = models.PositiveIntegerField()
    memo = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
