from django.contrib.auth import get_user_model

from .models import Notification

User = get_user_model()


def info(user: User, content: str):
    Notification.objects.create(
        user=user, content=content, level=Notification.Level.INFO
    )


def success(user: User, content: str):
    Notification.objects.create(
        user=user, content=content, level=Notification.Level.SUCCESS
    )


def warning(user: User, content: str):
    Notification.objects.create(
        user=user, content=content, level=Notification.Level.WARNING
    )


def error(user: User, content: str):
    Notification.objects.create(
        user=user, content=content, level=Notification.Level.ERROR
    )
