from pathlib import Path

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.track.models import Track


def upload_avatar_to(instance: "Profile", filename: str):
    ext = Path(filename).suffix
    return f"account/avatar/{instance.user.username}{ext}"


class Profile(models.Model):
    user: User = models.OneToOneField(User, on_delete=models.CASCADE)  # type: ignore
    age: int = models.PositiveIntegerField(blank=True, null=True)  # type: ignore
    default_sport = models.CharField(
        choices=Track.SportChoices.choices, null=True, blank=True, max_length=32
    )

    avatar = models.ImageField(
        blank=True, upload_to=upload_avatar_to, default="default-avatar.png"
    )

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def user_post_save(sender: type, instance: User, created, **kwargs):
    if not hasattr(instance, "profile"):
        Profile.objects.create(user=instance)
