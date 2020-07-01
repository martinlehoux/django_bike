from pathlib import Path
import uuid
from typing import List
from math import sqrt
from datetime import timedelta

from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .parsers import PARSERS


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


def source_file_path(track, filename):
    suffixes = "".join(Path(filename).suffixes)
    return (
        Path()
        / "track"
        / "source"
        / f"track_{track.name.lower()}_{track.uuid}{suffixes}"
    )


gpx_file_path = source_file_path  # TODO: depreciate


class Track(models.Model):
    class StateChoices(models.TextChoices):
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        ERROR = "error", "Error"

    uuid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(max_length=128)
    datetime = models.DateTimeField(blank=True, default=timezone.now)
    source_file = models.FileField(upload_to=source_file_path, blank=True, null=True)
    parser = models.CharField(
        max_length=32, choices=[(parser, parser) for parser in PARSERS.keys()]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    public = models.BooleanField(default=False)
    state = models.CharField(
        max_length=32, choices=StateChoices.choices, default=StateChoices.READY
    )

    @property
    def points_count(self) -> int:
        return self.point_set.count()

    def __str__(self):
        return f"{self.name} ({self.uuid})"

    def get_absolute_url(self):
        return reverse("track:detail", kwargs={"pk": self.pk})


class TrackStat:
    track: Track

    def __init__(self, track: Track):
        assert isinstance(track, Track)
        self.track = track

    def pos_ele(self) -> float:
        alt_cum = smoother(TrackData(self.track).alt_cum())
        if alt_cum:
            return alt_cum[-1]
        return 0.0

    def duration(self) -> timedelta:
        duration = TrackData(self.track).time()
        if duration:
            return duration[-1]
        return timedelta()

    def distance(self) -> float:
        """km"""
        distance = TrackData(self.track).dist()
        if distance:
            return distance[-1]
        return 0.0

    def mean_speed(self) -> float:
        """km/h"""
        duration = self.duration()
        distance = self.distance()
        if duration:
            return distance / duration.total_seconds() * 3600
        return None


class TrackData:
    track: Track

    def __init__(self, track: Track):
        assert isinstance(track, Track)
        self.track = track

    def time(self) -> List[timedelta]:
        return [point.time for point in self.track.point_set.all()]

    def lon(self) -> List[float]:
        return [point.lon for point in self.track.point_set.all()]

    def lat(self) -> List[float]:
        return [point.lat for point in self.track.point_set.all()]

    def x(self) -> List[float]:
        return [point.x for point in self.track.point_set.all()]

    def y(self) -> List[float]:
        return [point.y for point in self.track.point_set.all()]

    def dist(self) -> List[float]:
        """km"""
        return [point.dist / 1000 for point in self.track.point_set.all()]

    def alt(self) -> List[float]:
        return [point.alt for point in self.track.point_set.all()]

    def alt_cum(self) -> List[float]:
        alt_cum = []
        points = self.track.point_set.all()
        for index, point in enumerate(points):
            previous = points[index - 1] if index > 0 else point
            alt_cum.append(
                max(point.alt - previous.alt, 0) + alt_cum[index - 1]
                if index > 0
                else 0
            )
        return alt_cum

    def slope(self) -> List[float]:
        slope = [0]
        points = self.track.point_set.all()
        for index, point in list(enumerate(points))[1:]:
            previous = points[index - 1]
            try:
                slope.append(
                    (point.alt - previous.alt)
                    / sqrt((point.x - previous.x) ** 2 + (point.y - previous.y) ** 2)
                    * 100
                )
            except ZeroDivisionError:
                slope.append(slope[-1])
        return slope

    def speed(self) -> List[float]:
        speed = [0]
        points = self.track.point_set.all()
        for index, point in list(enumerate(points))[1:]:
            previous = points[index - 1]
            if point.time == previous.time:
                speed.append(speed[-1])
            else:
                speed.append(
                    (point.dist - previous.dist)
                    / (point.time - previous.time).total_seconds()
                    * 3.6
                )
        return speed


def smoother(array: List[float], smooth_size: int = 30) -> List[float]:
    new_array = []
    for i in range(len(array)):
        start = max(i - smooth_size, 0)
        end = min(i + smooth_size, len(array))
        new_array.append(sum(array[start:end]) / len(array[start:end]))
    return new_array
