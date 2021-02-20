from typing import List
from xml.etree import ElementTree

from django.utils.dateparse import parse_datetime


class StravaGPXParser:
    def parse(self, file: bytes) -> List[dict]:
        xml = ElementTree.parse(file)
        root = xml.getroot()
        points = []
        for trkpt in root[1][2]:
            points.append(
                dict(
                    lat=float(trkpt.attrib["lat"]),
                    lon=float(trkpt.attrib["lon"]),
                    alt=float(trkpt[0].text),
                    dist=0.0,
                    time=parse_datetime(trkpt[1].text),  # UTC
                )
            )
        return points
