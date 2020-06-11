from pathlib import Path
import uuid
from typing import List

from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from .parsers.gpx.amazfit import AmazfitGPXParser


User = get_user_model()


class Point(models.Model):
    class Meta:
        ordering = ["time"]

    track = models.ForeignKey("track.Track", on_delete=models.CASCADE)
    lat = models.FloatField()
    lon = models.FloatField()
    time = models.DurationField()
    alt = models.FloatField(default=0)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    dist = models.FloatField(default=0)


def gpx_file_path(track, filename):
    return Path() / "track" / "gpx" / f"track_{track.name.lower()}_{track.uuid}.gpx"


class Track(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=128)
    datetime = models.DateTimeField(blank=True)
    gpx_file = models.FileField(upload_to=gpx_file_path, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    public = models.BooleanField(default=False)

    @property
    def points_count(self) -> int:
        return self.point_set.count()

    def __str__(self):
        return f"{self.name} ({self.uuid})"

    def get_absolute_url(self):
        return reverse("track-detail", kwargs={"pk": self.pk})

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.pk is None and self.gpx_file:
            parser = AmazfitGPXParser()
            points = parser.parse(self.gpx_file.file.open())
            self.datetime = points[0]["time"]
            super().save(
                force_insert=force_insert,
                force_update=force_update,
                using=using,
                update_fields=update_fields,
            )
            for point in points:
                point["time"] -= self.datetime
            Point.objects.bulk_create([Point(**point, track=self) for point in points])
        else:
            super().save(
                force_insert=force_insert,
                force_update=force_update,
                using=using,
                update_fields=update_fields,
            )

    @property
    def alt_dist_dataset(self) -> List[dict]:
        return list(
            self.point_set.extra(select={"x": "dist", "y": "alt"}).values("x", "y")
        )

