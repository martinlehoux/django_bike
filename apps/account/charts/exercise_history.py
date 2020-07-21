from django.db.models import Sum
from plotly import graph_objs as go

from apps.track.models import Track
from .base import BaseChart
from . import time_range_query


class TimeAggregate:
    WEEK_DAY = "datetime__week_day"
    DAY = "datetime__day"


class StatQuery:
    DISTANCE = "trackstat__distance"


class ExerciseHistoryChart(BaseChart):
    name = "Exercise History"
    x_title = TimeAggregate.DAY
    y_title = "Kilometers"

    def get_data(self):
        time_query = time_range_query.WeekTimeRange(self.now)
        tracks = Track.objects.filter(time_query.query)
        summary = tracks.values(TimeAggregate.WEEK_DAY).annotate(
            distance=Sum(StatQuery.DISTANCE)
        )
        x, y = time_query.fill_data(summary, TimeAggregate.WEEK_DAY, "distance")
        return [go.Bar(x=x, y=y, name=self.name,)]
