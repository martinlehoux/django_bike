from pathlib import Path
import csv
import uuid

from django.core.management.base import CommandParser, BaseCommand

from apps.track.models import Track, Point


class Command(BaseCommand):
    help = "Dumps track's points to CSV"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("track_pk", type=int)
        parser.add_argument("--output", "-o", type=Path, default=Path("."))

    def handle(self, track_pk: int, output: Path, *args, **options):
        try:
            track = Track.objects.get(pk=track_pk)
        except Track.DoesNotExist:
            print(f"Track {track_pk} not found")
            return

        with open(output / f"{uuid.uuid4()}.csv", "w") as file:
            writer = csv.writer(file)
            point: Point
            for point in track.point_set.all():
                writer.writerow([point.x, point.y, point.alt, point.time, point.dist])
