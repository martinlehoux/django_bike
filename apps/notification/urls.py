from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_notifications, name="notif"),
    path("<int:pk>", views.detail_notif, name="notif-detail"),
]
