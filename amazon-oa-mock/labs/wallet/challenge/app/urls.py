from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("api/state/", views.state),
    path("api/history/", views.history),
    path("api/transfer/", views.transfer),
]
