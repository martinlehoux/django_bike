import csv
from datetime import timedelta
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files import File
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_duration

from apps.main.utils import FileSystemTestCase, TestMixin

from .models import Point, Track, TrackData, TrackStat
from .tasks import haversine, track_parse_source


class TrackDataRealTest(FileSystemTestCase):
    user: User
    track1: Track

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.user = User.objects.create_user("Kagamino")
        cls.track1 = Track.objects.create(
            name="Track 1",
            parser="amazfit-gpx-parser",
            datetime=now,
            user=cls.user,
            source_file=File(
                open(Path(__file__).parent / "tests" / "track_zero_div.gpx")
            ),
        )
        track_parse_source(cls.track1.pk)

    def test_slope(self):
        data = TrackData(self.track1)
        data.slope()


class TrackStatRealTest(TestMixin, TestCase):
    track: Track

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.user = User.objects.create_user("Kagamino")
        cls.track = Track.objects.create(
            name="Track 1",
            datetime=now,
            user=cls.user,
        )
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
        stat = TrackStat(track=self.track)
        stat.compute()

        self.assertIsClose(stat.distance, 19.31, 0.05)
        self.assertAlmostEqual(
            stat.duration,
            timedelta(minutes=58, seconds=22),
            delta=timedelta(seconds=10),
        )
        self.assertIsClose(stat.mean_speed, 19.85, 0.05)
        self.assertIsClose(stat.pos_ele, 300, 0.05)


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


class TrackPermissionsTestCase(TestCase):
    user1: User
    user2: User

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user("Kagamino")
        cls.user2 = User.objects.create_user("Other")

    def test_view_permission(self):
        now = timezone.now()
        track = Track.objects.create(name="Track 1", datetime=now, user=self.user1)

        self.assertTrue(self.user1.has_perm("track.view_track", track))
        self.assertFalse(self.user2.has_perm("track.view_track", track))

        track.public = True
        track.save()

        self.assertTrue(self.user1.has_perm("track.view_track", track))
        self.assertTrue(self.user2.has_perm("track.view_track", track))

    def test_detail_view(self):
        now = timezone.now()
        res: HttpResponse
        track = Track.objects.create(name="Track 1", datetime=now, user=self.user1)
        url = reverse("track:detail", args=[track.pk])

        res = self.client.get(url)
        self.assertContains(res, track, status_code=403)

        self.client.force_login(self.user1)
        res = self.client.get(url)
        self.assertContains(res, "Track 1")

        self.client.force_login(self.user2)
        res = self.client.get(url)
        self.assertContains(res, track, status_code=403)

        track.public = True
        track.save()

        self.client.force_login(self.user1)
        res = self.client.get(url)
        self.assertContains(res, "Track 1")

        self.client.force_login(self.user2)
        res = self.client.get(url)
        self.assertContains(res, "Track 1")

    def test_track_list_view(self):
        now = timezone.now()
        res: HttpResponse
        track1 = Track.objects.create(name="Track 1", datetime=now, user=self.user1)
        track2_private = Track.objects.create(
            name="Track 2.1", datetime=now, user=self.user2
        )
        track2_public = Track.objects.create(
            name="Track 2.2", datetime=now, user=self.user2, public=True
        )
        url = reverse("track:list")

        res = self.client.get(url)
        self.assertNotContains(res, track1.name)
        self.assertNotContains(res, track2_private.name)
        self.assertContains(res, track2_public.name)

        self.client.force_login(self.user1)
        res = self.client.get(url)
        self.assertContains(res, track1.name)
        self.assertNotContains(res, track2_private.name)
        self.assertContains(res, track2_public.name)

        self.client.force_login(self.user2)
        res = self.client.get(url)
        self.assertNotContains(res, track1.name)
        self.assertContains(res, track2_private.name)
        self.assertContains(res, track2_public.name)


class TrackComputeTestCase(TestCase):
    def test_haversine(self):
        """Test the correct distance between Paris and New York"""
        dist = haversine(2.2770205, 48.8589507, -74.1197637, 40.6976637) / 1000
        ref_dist = 5834.0
        # A 10km diff is 0.17% error
        self.assertAlmostEqual(dist, ref_dist, delta=10.0)
