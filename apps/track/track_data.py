from datetime import timedelta
from math import atan, cos, sin, sqrt
from typing import List, Optional

import gpxpy
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from gpxpy.gpx import GPX, PointData

from .models import Track


class TrackData:
    MIN_POS_ELE = 8
    track: Track
    _gpx: GPX
    _points: List[PointData]

    def __init__(self, track: Track):
        assert isinstance(track, Track)
        self.track = track
        self._gpx = gpxpy.parse(track.source_file.open())
        self._points = self._gpx.get_points_data()

    def time(self) -> List[timedelta]:
        return [p.point.time - self.track.datetime for p in self._points]

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
        return [p.distance_from_start / 1000 for p in self._points]

    def alt(self) -> List[Optional[float]]:
        # TODO When empty ?
        return [p.point.elevation for p in self._points]

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
        """km / h"""
        speed = [0.0]
        for index, current in list(enumerate(self._points))[1:]:
            previous = self._points[index - 1]
            if current.point.time == previous.point.time:
                speed.append(speed[-1])
            elif current.point.time is None or previous.point.time is None:
                speed.append(speed[-1])
            else:
                speed.append(
                    (current.distance_from_start - previous.distance_from_start)
                    / (current.point.time - previous.point.time).total_seconds()
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
