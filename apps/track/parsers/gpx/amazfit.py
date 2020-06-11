from xml.etree import ElementTree
from typing import List

from django.utils.dateparse import parse_datetime


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
        return points
