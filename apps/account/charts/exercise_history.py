from datetime import datetime

from django.db.models import Sum
from django.utils import timezone
from plotly import graph_objs as go

from apps.track.models import Track

from . import time_range_query
from .base import BaseChart


class ExerciseHistoryChart(BaseChart):
    name = "Exercise History"
    time_range: type = time_range_query.WeekTimeRange
    x_title = ""
    y_title = "Kilometers"

    def __init__(
        self,
        user,
        time_range: type = time_range_query.WeekTimeRange,
        now: datetime = timezone.now(),
    ):
        self.time_range = time_range
        super().__init__(user, now)

    def get_data(self):
        time_query = self.time_range(self.now)
        tracks = Track.objects.filter(time_query.query)
        summary = tracks.values(time_query.time_aggregate).annotate(
            distance=Sum(time_query.stat_query)
        )
        x, y = time_query.fill_data(summary, time_query.time_aggregate, "distance")
        return [go.Bar(x=x, y=y, name=self.name)]
