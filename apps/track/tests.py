from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Track


class TrackPermissionsTestCase(TestCase):
    user1: User
    user2: User

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user("Kagamino")
        cls.user2 = User.objects.create_user("Other")

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
