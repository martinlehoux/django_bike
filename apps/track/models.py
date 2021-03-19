import uuid
from datetime import timedelta
from math import atan, cos, sin, sqrt
from pathlib import Path
from typing import List, Optional

import gpxpy
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from .parsers import PARSERS


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

    # Typing
    comment_set: Manager["Comment"]
    point_set: Manager["Point"]

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
    _point_set: QuerySet[Point]

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

    # SLOPE
    def slope(self) -> List[float]:
        method = settings.METHODS_VERSION.get("slope")
        return getattr(self, method)()

    def slope_v1(self) -> List[float]:
        slope = [0.0]
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

    def slope_v2(self) -> List[float]:
        points = self._point_set
        slope: List[Optional[float]] = [None for _ in range(len(points))]
        slope[0] = 0.0
        # Every 30 points
        i = 30  #  TODO May be false
        for i in range(30, len(points), 30):
            point = points[i]
            previous: Point = points[i - 30]
            try:
                slope[i] = (
                    (point.alt - previous.alt)
                    / sqrt((point.x - previous.x) ** 2 + (point.y - previous.y) ** 2)
                    * 100
                )
            except ZeroDivisionError:
                slope[i] = slope[i - 30]
        # Fill last point
        if i < len(points) - 1:
            point = points.last()
            if point is None:
                slope[-1] = 0.0
            else:
                previous: Point = points[i]
                try:
                    slope[-1] = (
                        (point.alt - previous.alt)
                        / sqrt(
                            (point.x - previous.x) ** 2 + (point.y - previous.y) ** 2
                        )
                        * 100
                    )
                except ZeroDivisionError:
                    slope[-1] = slope[i]
        # Complete
        for i in range(len(slope)):
            if slope[i] is None:
                last = i - i % 30
                next = min(len(slope) - 1, i - i % 30 + 30)
                slope[i] = (
                    1 / 30 * (slope[last] * (i - last) + slope[next] * (next - i))
                )
        return slope

    def speed(self) -> List[float]:
        speed = [0.0]
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
        acceleration = [0.0]
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
        MASS = 80.0  # kg # TODO
        GRAVITY = 9.87  # m/s2
        AIR_DENSITY = 1.225  # kg/m3
        DRAG_COEF = 0.9  # TODO
        WIND_SURFACE = 0.44704  # m2 # TODO
        # W = kg.m2/s3
        power = [0.0]
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
    objects: Manager["TrackStat"]

    track: Track = models.OneToOneField(
        "track.Track",
        on_delete=models.CASCADE,
    )  # type: ignore
    pos_ele = models.FloatField("positive elevation", default=0.0, blank=True)  # m
    duration = models.DurationField(default=timedelta(), blank=True)
    distance = models.FloatField(default=0.0, blank=True)  # m
    mean_speed = models.FloatField(default=0.0, blank=True)  # m/s

    def __str__(self) -> str:
        return f"TrackStat for {self.track.uuid}"

    def compute(self):
        gpx = gpxpy.parse(self.track.source_file.open())
        moving_data = gpx.get_moving_data()
        self.pos_ele = gpx.get_uphill_downhill().uphill
        self.duration = timedelta(seconds=moving_data.moving_time)
        self.distance = moving_data.moving_distance
        self.mean_speed = self.distance / self.duration.total_seconds()

    @property
    def distance_km(self) -> float:
        return self.distance / 1000

    @property
    def mean_speed_km_h(self) -> float:
        return self.mean_speed * 3.6


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey("track.Track", on_delete=models.CASCADE)
    text = models.TextField(blank=False, validators=[MaxLengthValidator(200)])
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment: {self.author} @ {self.track} @ {self.datetime}"


class Like(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "track"], name="like_unique")
        ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey("track.Track", on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Like: {self.user} @ {self.track} @ {self.datetime}"


@receiver(post_save, sender=Track)
def track_post_save(sender, instance: Track, created: bool, *args, **kwargs):
    if not TrackStat.objects.filter(track=instance).exists():
        track_stat = TrackStat(track=instance)
        track_stat.compute()
        track_stat.save()
    if created:
        gpx = gpxpy.parse(instance.source_file.open())
        instance.datetime = gpx.get_time_bounds().start_time
        instance.save()
