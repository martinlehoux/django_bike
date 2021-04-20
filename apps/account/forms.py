from typing import Callable

from django import forms
from django.conf import settings
from django.http import QueryDict
from PIL import Image

from .charts.time_range_query import (
    MonthTimeRange,
    TimeRangeQuery,
    WeekTimeRange,
    YearTimeRange,
)
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


class ExerciseHistoryForm(forms.Form):
    TIME_RANGE_CHOICES = {
        "week": WeekTimeRange,
        "month": MonthTimeRange,
        "year": YearTimeRange,
    }
    time_range = forms.ChoiceField(
        choices=[(key, key) for key in TIME_RANGE_CHOICES.keys()],
    )

    @property
    def time_range_choice(self) -> Callable[..., TimeRangeQuery]:
        assert self.is_valid()
        return self.TIME_RANGE_CHOICES[self.cleaned_data["time_range"]]

    def __init__(self, data: QueryDict, *args, **kwargs):
        data = data.copy()
        if not data.get("time_range"):
            data["time_range"] = "week"
        super().__init__(data, *args, **kwargs)
