from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("api/state/", views.state),
    path("api/actors/<int:actor_id>/follow/", views.follow),
    path("api/actors/<int:actor_id>/unfollow/", views.unfollow),
    path("api/movies/", views.release),
    path("api/notifications/<int:notification_id>/read/", views.read),
]
