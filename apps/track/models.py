from pathlib import Path
import uuid
from typing import List
from math import sqrt, cos, sin, atan
from datetime import timedelta

from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save
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


class TrackData:
    DIST_FACTOR = 0.88
    MIN_POS_ELE = 8
    track: Track
    _point_set: models.QuerySet

    def __init__(self, track: Track):
        assert isinstance(track, Track)
        self.track = track
        self._point_set = self.track.point_set.all()

    def time(self) -> List[timedelta]:
        return [point.time for point in self._point_set]

    def lon(self) -> List[float]:
        return [point.lon for point in self._point_set]

    def lat(self) -> List[float]:
        return [point.lat for point in self._point_set]

    def x(self) -> List[float]:
        return [point.x for point in self._point_set]

    def y(self) -> List[float]:
        return [point.y for point in self._point_set]

    def dist(self) -> List[float]:
        """km"""
        return [point.dist * self.DIST_FACTOR / 1000 for point in self._point_set]

    def alt(self) -> List[float]:
        return [point.alt for point in self._point_set]

    def alt_cum(self) -> List[float]:
        # https://www.gpsvisualizer.com/tutorials/elevation_gain.html

        points = self._point_set
        alt_cum = []
        if not points:
            return []
        last_low_alt = points[0].alt
        for index, point in enumerate(points):
            if index == 0:
                alt_cum.append(0)
            elif point.alt >= last_low_alt + self.MIN_POS_ELE:
                alt_cum.append(point.alt - last_low_alt + alt_cum[index - 1])
                last_low_alt = point.alt
            else:
                alt_cum.append(alt_cum[index - 1])
                if point.alt < last_low_alt:
                    last_low_alt = min(point.alt, last_low_alt)
        return alt_cum

    def slope(self) -> List[float]:
        slope = [0]
        points = self._point_set
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
        points = self._point_set
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

    def acceleration(self) -> List[float]:
        acceleration = [0]
        speed = [s / 3.6 for s in self.speed()]
        points = self._point_set
        for index, point in list(enumerate(points))[1:]:
            previous = points[index - 1]
            if point.time == previous.time:
                acceleration.append(acceleration[-1])
            else:
                acceleration.append(
                    (speed[index] - speed[index - 1])
                    / (point.time - previous.time).total_seconds()
                )
        return acceleration

    def power(self) -> List[float]:
        ROLLING_RESISTANCE = 0.005  # TODO
        MASS = 80  # kg # TODO
        GRAVITY = 9.87  # m/s2
        AIR_DENSITY = 1.225  # kg/m3
        DRAG_COEF = 0.9  # TODO
        WIND_SURFACE = 0.44704  # m2 # TODO
        # W = kg.m2/s3
        power = [0]
        slope = self.slope()
        speed = [s / 3.6 for s in self.speed()]
        acceleration = self.acceleration()
        points = self._point_set
        for index, point in list(enumerate(points))[1:]:
            weight = MASS * GRAVITY  # N = kg * m/s2
            normal = weight * cos(slope[index] / 100)  # N
            rolling_resistance = (
                ROLLING_RESISTANCE * normal * speed[index]
            )  # W = N * m/s
            wind = (
                0.5 * AIR_DENSITY * speed[index] ** 3 * DRAG_COEF * WIND_SURFACE
            )  # W = kg/m3 * m3/s3 * m2
            gravity = (
                weight * speed[index] * sin(atan(slope[index] / 100))
            )  # W = N * m/s
            accel = MASS * speed[index] * acceleration[index]  # W = kg * m/s * m/s2
            power.append(rolling_resistance + wind + gravity + accel)
        return power


class TrackStat(models.Model):
    track: Track = models.OneToOneField("track.Track", on_delete=models.CASCADE)
    pos_ele = models.FloatField("positive elevation", default=0.0, blank=True)
    duration = models.DurationField(default=timedelta(), blank=True)
    distance = models.FloatField(default=0.0, blank=True)
    mean_speed = models.FloatField(default=0.0, blank=True)

    def compute(self):
        data = TrackData(self.track)
        self.pos_ele = self._pos_ele(data)
        self.duration = self._duration(data)
        self.distance = self._distance(data)
        self.mean_speed = self._mean_speed(data)

    def _pos_ele(self, data: TrackData) -> float:
        alt_cum = smoother(data.alt_cum())
        if alt_cum:
            return alt_cum[-1]
        return 0.0

    def _duration(self, data: TrackData) -> timedelta:
        duration = data.time()
        if duration:
            return duration[-1]
        return timedelta()

    def _distance(self, data: TrackData) -> float:
        """km"""
        distance = data.dist()
        if distance:
            return distance[-1]
        return 0.0

    def _mean_speed(self, data: TrackData) -> float:
        """km/h"""
        duration = self._duration(data)
        distance = self._distance(data)
        if duration:
            return distance / duration.total_seconds() * 3600
        return 0.0


def smoother(array: List[float], smooth_size: int = 30) -> List[float]:
    new_array = []
    for i in range(len(array)):
        start = max(i - smooth_size, 0)
        end = min(i + smooth_size, len(array))
        new_array.append(sum(array[start:end]) / len(array[start:end]))
    return new_array


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey("track.Track", on_delete=models.CASCADE)
    text = models.TextField(blank=False)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment: {self.author} @ {self.track} @ {self.datetime}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey("track.Track", on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Like: {self.user} @ {self.track} @ {self.datetime}"


@receiver(post_save, sender=Track)
def track_pre_save(sender, instance: Track, *args, **kwargs):
    if not TrackStat.objects.filter(track=instance).exists():
        TrackStat.objects.create(track=instance)
