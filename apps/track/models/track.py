import uuid
from pathlib import Path

import gpxpy
import srtm
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils import timezone


def source_file_path(track, filename):
    return Path() / "track" / "source" / f"{track.uuid}.gpx"


class Track(models.Model):
    class StateChoices(models.TextChoices):
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        ERROR = "error", "Error"

    uuid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=128)
    datetime = models.DateTimeField(blank=True, default=timezone.now)
    source_file = models.FileField(upload_to=source_file_path, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    public = models.BooleanField(default=False)
    state = models.CharField(
        max_length=32, choices=StateChoices.choices, default=StateChoices.READY
    )

    # Typing
    comment_set: models.Manager["Comment"]
    point_set: models.Manager["Point"]
    objects: models.Manager["Track"]
    trackstat: "TrackStat"

    @property
    def points_count(self) -> int:
        return self.point_set.count()

    def __str__(self):
        return f"{self.name} ({self.uuid})"

    def get_absolute_url(self):
        return reverse("track:detail", kwargs={"pk": self.pk})

    def parse_source(self):
        elevation_data = srtm.get_data()
        gpx = gpxpy.parse(self.source_file.open())
        elevation_data.add_elevations(
            gpx, smooth=True, gpx_smooth_no=settings.GPX_SMOOTH_NO
        )
        file = ContentFile(gpx.to_xml("1.1"))
        filename = self.source_file.name
        self.source_file.delete()
        self.source_file.save(filename, file)
        self.datetime = gpx.get_time_bounds().start_time
        self.state = Track.StateChoices.READY
        self.save()
