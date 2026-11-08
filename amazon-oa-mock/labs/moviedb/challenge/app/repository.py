from core import Problem
from .models import Actor, Follow


def actor_by_id(actor_id):
    actor = Actor.objects.filter(pk=actor_id).first()
    if actor is None:
        raise Problem("ACTOR_NOT_FOUND", 404)
    return actor


def persist_follow(user, actor):
    follow = Follow(user=user, actor=actor)
    # Save is handled by the caller.
    return follow
