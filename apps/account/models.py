from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(blank=True, null=True)

    avatar = models.ImageField(blank=True, upload_to="avatars")

    def __str__(self):
        return str(self.user)
