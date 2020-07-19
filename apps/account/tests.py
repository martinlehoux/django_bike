from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model, models
from PIL import Image

from .forms import AvatarForm

User = get_user_model()
models.User


class ProfileTestCase(TestCase):
    def test_default_profile(self):
        user = User.objects.create_user("username", "email@email.com")

        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.avatar.name, "default-avatar.png")
        avatar = Image.open(user.profile.avatar.path)
        self.assertEqual(avatar.size, settings.AVATAR_SIZE)

    def test_upload_avatar(self):
        user = User.objects.create_user("username", "email@email.com")
        file = Image.new("RGB", (600, 1000))
        form = AvatarForm(data={"avatar": file}, instance=user.profile)
        form.save()

        avatar = Image.open(user.profile.avatar.path)
        self.assertEqual(avatar.size, settings.AVATAR_SIZE)
