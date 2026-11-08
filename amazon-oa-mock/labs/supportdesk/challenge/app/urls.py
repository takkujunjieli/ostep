from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("api/state/", views.state),
    path("api/tickets/", views.tickets),
    path("api/tickets/<int:ticket_id>/", views.detail),
    path("api/tickets/<int:ticket_id>/reply/", views.reply),
    path("api/tickets/<int:ticket_id>/close/", views.close),
]
