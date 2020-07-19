from django import forms
from django.conf import settings
from PIL import Image

from .models import Profile


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]

    def save(self):
        AVATAR_WIDTH, AVATAR_HEIGHT = settings.AVATAR_SIZE
        profile = super().save()
        avatar: Image.Image = Image.open(profile.avatar)
        ratio = min(avatar.width / AVATAR_WIDTH, avatar.height / AVATAR_HEIGHT)
        cropped = avatar.crop(
            (
                (avatar.width - AVATAR_WIDTH * ratio) / 2,
                (avatar.height - AVATAR_HEIGHT * ratio) / 2,
                (avatar.width + AVATAR_WIDTH * ratio) / 2,
                (avatar.height + AVATAR_HEIGHT * ratio) / 2,
            )
        )
        resized = cropped.resize((AVATAR_WIDTH, AVATAR_HEIGHT), Image.ANTIALIAS)
        resized.save(profile.avatar.path)
        return profile
