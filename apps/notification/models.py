from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver


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

    @property
    def json(self):
        return {
            "content": self.content,
            "pk": self.pk,
            "level": self.level,
            "datetime": self.datetime.isoformat(),
        }


@receiver(models.signals.post_save, sender=Notification)
def notification_post_save(sender, instance, created, *args, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            instance.user.username,
            {"type": "new_notification", "notification": instance.json},
        )
