from .models import Follow, Notification


def notify_followers(movie):
    user_ids = Follow.objects.filter(actor__in=movie.cast.all()).values_list("user_id", flat=True).distinct()
    for user_id in user_ids:
        Notification.objects.get_or_create(user_id=user_id, movie=movie)


def unread_count(user):
    return Notification.objects.filter(user=user, is_read=False).count()
