from xml.etree import ElementTree
from typing import List
from math import radians, cos, sin, asin, sqrt
import random

from django.utils.dateparse import parse_datetime


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


class AmazfitGPXParser:
    def parse(self, file: bytes) -> List[dict]:
        xml = ElementTree.parse(file)
        root = xml.getroot()
        points = []
        for trkpt in root[0][0]:
            points.append(
                dict(
                    lat=float(trkpt.attrib["lat"]),
                    lon=float(trkpt.attrib["lon"]),
                    alt=0.0,
                    dist=0.0,
                    time=parse_datetime(trkpt[1].text),  # UTC
                )
            )
        points = self.compute_coordinates(points)
        points = self.compute_alt(points)
        points = self.compute_dist(points)
        return points

    def compute_coordinates(self, points: List[dict]) -> List[dict]:
        for point in points:
            point["x"] = haversine(points[0]["lon"], 0, point["lon"], 0)
            point["y"] = haversine(0, points[0]["lat"], 0, point["lat"])
        return points

    def compute_dist(self, points: List[dict]) -> List[dict]:
        for index, point in enumerate(points):
            previous = points[index - 1] if index > 0 else point
            point["dist"] = (
                sqrt(
                    (point["x"] - previous["x"]) ** 2
                    + (point["y"] - previous["y"]) ** 2
                    + (point["alt"] - previous["alt"]) ** 2
                )
                + previous["dist"]
            )
        return points

    def compute_alt(self, points: List[dict]) -> List[dict]:
        # TODO: Use API
        for index, point in enumerate(points):
            previous = points[index - 1] if index > 0 else point
            point["alt"] = previous["alt"] + random.random() * 1
        return points
