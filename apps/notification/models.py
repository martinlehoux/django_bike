from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    class Level(models.TextChoices):
        INFO = "is-info"
        SUCCESS = "is-success"
        WARNING = "is-warning"
        ERROR = "is-danger"

    datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    content = models.CharField(max_length=2000)
    level = models.CharField(max_length=64, choices=Level.choices, default=Level.INFO)
