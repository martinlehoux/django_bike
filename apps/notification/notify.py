from typing import Union

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser

from .models import Notification

RequestUser = Union[AbstractBaseUser, AnonymousUser]


def info(user: RequestUser, content: str):
    Notification.objects.create(
        user=user, content=content, level=Notification.Level.INFO
    )


def success(user: RequestUser, content: str):
    Notification.objects.create(
        user=user, content=content, level=Notification.Level.SUCCESS
    )


def warning(user: RequestUser, content: str):
    Notification.objects.create(
        user=user, content=content, level=Notification.Level.WARNING
    )


def error(user: RequestUser, content: str):
    Notification.objects.create(
        user=user, content=content, level=Notification.Level.ERROR
    )
