from pathlib import Path

from django.utils import timezone
from django.test import TestCase
from django.core.files import File
from django.contrib.auth import get_user_model

from apps.main.utils import FileSystemTestCase
from .models import Track, Point, TrackData
from .tasks import track_parse_source


User = get_user_model()


class TrackModelTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Kagamino")


class TrackDataTestCase(TestCase):
    user: User
    track1: Track
    track2: Track

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.user = User.objects.create_user("Kagamino")
        cls.track1 = Track.objects.create(name="Track 1", datetime=now, user=cls.user)
        for i in range(20):
            Point(
                track=cls.track1,
                lat=0,
                lon=0,
                time=timezone.timedelta(seconds=i),
                alt=i % 10,
                dist=i,
            ).save()

    def test_cum_alt(self):
        data1 = TrackData(self.track1)
        self.assertListEqual(
            data1.alt_cum(),
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
        )


class TrackDataRealTest(FileSystemTestCase):
    user: User
    track1: Track

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.user = User.objects.create_user("Kagamino")
        cls.track1 = Track.objects.create(
            name="Track 1",
            datetime=now,
            user=cls.user,
            source_file=File(
                open(Path(__file__).parent / "tests" / "track_zero_div.gpx")
            ),
        )
        track_parse_source(cls.track1.pk, "amazfit-gpx-parser")

    def test_slope(self):
        data = TrackData(self.track1)
        data.slope()


class PointModelTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Kagamino")

    def test_track_point_default_ordering(self):
        now = timezone.now()
        track = Track.objects.create(name="Track 1", datetime=now, user=self.user)
        point2 = Point.objects.create(
            track=track, lat=0, lon=0, time=timezone.timedelta(seconds=2)
        )
        point1 = Point.objects.create(
            track=track, lat=0, lon=0, time=timezone.timedelta(seconds=1)
        )
        self.assertGreater(point1.pk, point2.pk)
        self.assertEqual(track.point_set.first(), point1)
