from django.conf import settings
from django.db import models


class Ticket(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    description = models.TextField()
    status = models.CharField(max_length=12, default="open", choices=[("open", "Open"), ("closed", "Closed")])
    created_at = models.DateTimeField(auto_now_add=True)


class Reply(models.Model):
    ticket = models.ForeignKey(Ticket, related_name="replies", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
