from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from PIL import Image

from apps.track.models import Track

from .charts.exercise_history import ExerciseHistoryChart
from .forms import AvatarForm, MonthTimeRange, WeekTimeRange


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


class TrackProfileTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Kagamino")

    def test_track_time_stat(self):
        now = datetime(2020, 7, 15, 12, tzinfo=pytz.utc)
        self.assertEqual(now.weekday(), 2)  # Wednesday

        for i in range(100):
            track = Track.objects.create(
                name="Track 1", datetime=now - timedelta(days=i // 2), user=self.user
            )
            track.trackstat.distance = 10 * (i % 3 + 1)
            track.trackstat.save()

        # This week
        chart = ExerciseHistoryChart(self.user, WeekTimeRange, now)
        data = chart.get_data()[0]

        self.assertEqual(
            data.x,
            (
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ),
        )
        self.assertEqual(data.y, (0, 0, 50.0, 40.0, 30.0, 0, 0))

        # This month
        chart = ExerciseHistoryChart(self.user, MonthTimeRange, now)
        data = chart.get_data()[0]
        self.assertEqual(data.x, tuple(range(1, 32)))
        self.assertEqual(
            data.y,
            (
                0,
                50.0,
                40.0,
                30.0,
                50.0,
                40.0,
                30.0,
                50.0,
                40.0,
                30.0,
                50.0,
                40.0,
                30.0,
                50.0,
                40.0,
                30.0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ),
        )
