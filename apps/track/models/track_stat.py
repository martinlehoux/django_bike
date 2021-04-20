from datetime import timedelta

import gpxpy
from django.db import models


class TrackStat(models.Model):
    objects: models.Manager["TrackStat"]

    track: "Track" = models.OneToOneField(
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
