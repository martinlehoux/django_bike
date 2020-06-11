from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Track, Point


User = get_user_model()


class TrackModelTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("Kagamino")

    def test_track_alt_dist_dataset(self):
        now = timezone.now()
        track = Track.objects.create(name="Track 1", datetime=now, user=self.user)
        for i in range(10):
            Point(
                track=track,
                lat=0,
                lon=0,
                time=timezone.timedelta(seconds=i),
                alt=i ** 2,
                dist=i,
            ).save()
        dataset = track.alt_dist_dataset
        self.assertEqual(len(dataset), 10)
        self.assertEqual(dataset[0], {"x": 0, "y": 0})
        self.assertEqual(dataset[9], {"x": 9, "y": 81})


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
