from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


def upload_avatar_to(instance: User, filename: str):
    ext = Path(filename).suffix
    return f"account/avatar/{instance.user.username}{ext}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(blank=True, null=True)

    avatar = models.ImageField(
        blank=True, upload_to=upload_avatar_to, default="default-avatar.png"
    )

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def user_post_save(sender: type, instance: User, created, **kwargs):
    if not hasattr(instance, "profile"):
        Profile.objects.create(user=instance)
