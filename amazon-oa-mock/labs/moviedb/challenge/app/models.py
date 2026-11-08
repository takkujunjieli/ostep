from django.conf import settings
from django.db import models


class Actor(models.Model):
    name = models.CharField(max_length=120)


class Movie(models.Model):
    title = models.CharField(max_length=160)
    cast = models.ManyToManyField(Actor, related_name="movies")


class Follow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "actor"], name="unique_follow")]


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "movie"], name="unique_movie_notification")]
