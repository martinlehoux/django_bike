from pathlib import Path
import csv
from datetime import timedelta

from django.utils import timezone
from django.test import TestCase
from django.core.files import File
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_duration

from apps.main.utils import FileSystemTestCase, TestMixin
from .models import Track, Point, TrackData, TrackStat
from .tasks import track_parse_source


User = get_user_model()


class TrackModelTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Kagamino")


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
        track_parse_source(cls.track1.pk, "amazfit-gpx-parser", next_task=False)

    def test_slope(self):
        data = TrackData(self.track1)
        data.slope()


class TrackStatRealTest(TestMixin, TestCase):
    track: Track

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.user = User.objects.create_user("Kagamino")
        cls.track = Track.objects.create(name="Track 1", datetime=now, user=cls.user,)
        with open(
            Path(__file__).parent
            / "tests"
            / "c9454a76-4d06-4fea-bc54-2ced607f75bf.csv",
            "r",
        ) as file:
            reader = csv.reader(file)
            Point.objects.bulk_create(
                [
                    Point(
                        lat=0,
                        lon=0,
                        x=row[0],
                        y=row[1],
                        alt=row[2],
                        time=parse_duration(row[3]),
                        dist=row[4],
                        track=cls.track,
                    )
                    for row in reader
                ]
            )

    def test_stat_values(self):
        stat = TrackStat(self.track)

        self.assertIsClose(stat.distance(), 19.31, 0.05)
        self.assertAlmostEquals(
            stat.duration(),
            timedelta(minutes=58, seconds=22),
            delta=timedelta(seconds=10),
        )
        self.assertIsClose(stat.mean_speed(), 19.85, 0.05)
        self.assertIsClose(stat.pos_ele(), 300, 0.05)


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
