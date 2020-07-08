from .gpx.amazfit import AmazfitGPXParser
from .gpx.strava import StravaGPXParser

PARSERS = {
    "amazfit-gpx-parser": AmazfitGPXParser,
    "strava-gpx-parser": StravaGPXParser,
}
