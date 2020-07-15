from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(r"ws/notification/", consumers.NotificationConsumer),
]
