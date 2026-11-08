from django.db import transaction

from core import Problem, positive_int, text
from . import notifications, repository
from .models import Follow, Movie, Notification


@transaction.atomic
def follow_actor(user, actor_id):
    actor = repository.actor_by_id(actor_id)
    if Follow.objects.filter(user=user, actor=actor).exists():
        raise Problem("ALREADY_FOLLOWING", 400)
    return repository.persist_follow(user, actor)


def unfollow_actor(user, actor_id):
    repository.actor_by_id(actor_id)
    follow = Follow.objects.filter(user=user, actor_id=actor_id).first()
    if follow is None:
        raise Problem("FOLLOW_NOT_FOUND", 404)
    follow.delete()


@transaction.atomic
def release_movie(user, title, cast_ids):
    if not user.is_staff:
        raise Problem("ADMIN_REQUIRED", 403)
    title = text(title, 160)
    if not isinstance(cast_ids, list) or not cast_ids:
        raise Problem("INVALID_CAST")
    cast = [repository.actor_by_id(positive_int(actor_id)) for actor_id in set(cast_ids)]
    movie = Movie.objects.create(title=title)
    movie.cast.set(cast)
    notifications.notify_followers(movie)
    return movie


def mark_read(user, notification_id):
    notification = Notification.objects.filter(pk=notification_id, user=user).first()
    if notification is None:
        raise Problem("NOTIFICATION_NOT_FOUND", 404)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return notification
