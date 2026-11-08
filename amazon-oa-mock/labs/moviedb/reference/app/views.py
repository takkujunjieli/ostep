from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from core import endpoint, positive_int
from . import notifications, services
from .models import Actor, Follow, Movie, Notification


@login_required
def home(request):
    panels = '''<section><h2>Follow actors</h2>
    <form data-api="/api/actors/{actor_id}/follow/"><label>Actor ID</label><input name="actor_id" type="number" value="1" min="1" required><button>Follow</button></form>
    <form data-api="/api/actors/{actor_id}/unfollow/"><label>Actor ID</label><input name="actor_id" type="number" value="1" min="1" required><button>Unfollow</button></form>
    <hr><h2>Release a movie · admin</h2><form data-api="/api/movies/">
    <label>Title</label><input name="title" value="New Horizon" required>
    <label>Cast IDs (comma separated)</label><input name="cast_ids" value="1,2" required><button>Release movie</button></form>
    <hr><h2>Notifications</h2><form data-api="/api/notifications/{notification_id}/read/">
    <label>Notification ID</label><input name="notification_id" type="number" min="1" required><button>Mark as read</button></form></section>'''
    return render(request, "dashboard.html", {"title": "MovieDB", "description": "Follow actors and keep up with new releases. Use admin to publish a movie.", "panels": panels})


@endpoint("GET")
def state(request, data):
    return JsonResponse({
        "actors": list(Actor.objects.order_by("id").values()),
        "movies": list(Movie.objects.order_by("id").values("id", "title")),
        "following": list(Follow.objects.filter(user=request.user).order_by("id").values("id", "actor_id")),
        "notifications": list(Notification.objects.filter(user=request.user).order_by("id").values("id", "movie_id", "is_read")),
        "unread_count": notifications.unread_count(request.user),
    })


@endpoint("POST")
def follow(request, data, actor_id):
    result = services.follow_actor(request.user, actor_id)
    return JsonResponse({"id": result.pk, "actor_id": actor_id}, status=201)


@endpoint("POST")
def unfollow(request, data, actor_id):
    services.unfollow_actor(request.user, actor_id)
    return JsonResponse({"ok": True})


@endpoint("POST")
def release(request, data):
    movie = services.release_movie(request.user, data.get("title"), data.get("cast_ids"))
    return JsonResponse({"id": movie.pk, "title": movie.title}, status=201)


@endpoint("POST")
def read(request, data, notification_id):
    result = services.mark_read(request.user, positive_int(notification_id))
    return JsonResponse({"id": result.pk, "is_read": result.is_read})
