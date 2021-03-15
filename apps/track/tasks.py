import time
from math import asin, cos, radians, sin, sqrt
from typing import List
from xml.etree.ElementTree import ParseError

import celery
import requests
from celery import (
    chain,  # https://docs.celeryproject.org/en/stable/userguide/canvas.html
)
from celery.utils.log import get_task_logger
from django.conf import settings

from apps.notification import notify

from .models import Point, Track, TrackStat
from .parsers import PARSERS

logger = get_task_logger(__name__)


def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Args:
        lon: Longitude in decimal degrees
        lat: Latitude in decimal degrees
    Returns:
        meters: Curve distance between 1 and 2
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    meters = 6371 * c * 1000
    return meters


def track_error(track: Track, message: str, err: Exception):
    logger.error(message)
    track.state = Track.StateChoices.ERROR
    track.save()
    notify.error(
        track.user,
        f"An error has occured while processing {track} track: {err}",
    )
    raise err


@celery.shared_task
def track_clear_points(track_pk: int) -> int:
    track = Track.objects.get(pk=track_pk)
    track.point_set.delete()
    return track_pk


@celery.shared_task
def track_parse_source(track_pk: int) -> int:
    track = Track.objects.get(pk=track_pk)
    parser = PARSERS[track.parser]()
    track.state = Track.StateChoices.PROCESSING
    track.save()
    try:
        points = parser.parse(track.source_file.file.open())
        track.datetime = points[0]["time"]
        track.save()
        for point in points:
            point["time"] -= track.datetime
        Point.objects.bulk_create([Point(**point, track=track) for point in points])
        return track_pk
    except ParseError as err:
        track_error(track, f"Failed to parse {track} source file: {err}", err)


@celery.shared_task
def track_compute_coordinates(track_pk: int) -> int:
    track = Track.objects.get(pk=track_pk)
    track.state = Track.StateChoices.PROCESSING
    track.save()
    points: List[Point] = track.point_set.all()
    for point in points:
        point.x = haversine(points[0].lon, 0, point.lon, 0)
        point.y = haversine(0, points[0].lat, 0, point.lat)
    Point.objects.bulk_update(points, ["x", "y"], batch_size=100)
    return track_pk


@celery.shared_task
def track_retrieve_alt(track_pk: int) -> int:
    """Use JAWG API to get Altitudes
    Batch size is 500
    """
    track = Track.objects.get(pk=track_pk)
    track.state = Track.StateChoices.PROCESSING
    track.save()
    points = track.point_set.all()
    try:
        for i in range(len(points) // 500 + 1):
            time.sleep(1)  # API rate limit
            logger.info("Get altitudes for points %d to %d", i * 500, i * 500 + 499)
            token = settings.JAWG_TOKEN
            response = requests.post(
                f"https://api.jawg.io/elevations/locations?access-token={token}",
                json={
                    "locations": "|".join(
                        f"{point.lat},{point.lon}"
                        for point in points[i * 500 : (i + 1) * 500]  # noqa: E203
                    )
                },
            )
            for j, data in enumerate(response.json()):
                try:
                    points[i * 500 + j].alt = data["elevation"]
                except TypeError:
                    logger.error(response.json())
                    break
        Point.objects.bulk_update(points, ["alt"], batch_size=100)
    except Exception as err:
        track_error(track, f"Failed to load latitudes for track {track}: {err}", err)
    return track_pk


@celery.shared_task
def track_compute_dist(track_pk: int) -> int:
    track = Track.objects.get(pk=track_pk)
    track.state = Track.StateChoices.PROCESSING
    track.save()
    points = track.point_set.all()
    for index, point in enumerate(points):
        previous: Point = points[index - 1] if index > 0 else point
        point.dist = (
            sqrt(
                (point.x - previous.x) ** 2
                + (point.y - previous.y) ** 2
                + (point.alt - previous.alt) ** 2
            )
            + previous.dist
        )
    Point.objects.bulk_update(points, ["dist"], batch_size=100)
    return track_pk


@celery.shared_task
def track_compute_stat(track_pk: int):
    track = Track.objects.get(pk=track_pk)
    try:
        track.trackstat
    except TrackStat.DoesNotExist:
        track.trackstat = TrackStat(track=track)
    track.trackstat.compute()
    track.trackstat.save()
    return track_pk


@celery.shared_task
def track_state_ready(track_pk: int) -> int:
    track = Track.objects.get(pk=track_pk)
    track.state = Track.StateChoices.READY
    track.save()
    notify.success(track.user, f"{track.name} track is ready")
    return track_pk


def track_compute_trace(track_pk: int):
    return chain(
        track_parse_source.s(track_pk),
        track_compute_coordinates.s(),
        track_retrieve_alt.s(),
        track_compute_dist.s(),
    )
