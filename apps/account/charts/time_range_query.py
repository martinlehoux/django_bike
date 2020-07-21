from datetime import timedelta, datetime
from typing import List, Tuple
import calendar

from django.db.models import Q, QuerySet
from django.utils import timezone


class TimeRangeQuery:
    now: datetime

    def __init__(self, now: datetime = timezone.now()):
        self.now = now

    @property
    def query(self) -> Q:
        raise NotImplementedError

    def fill_data(
        self, summary: QuerySet, key: str, value: str
    ) -> Tuple[List[float], List[float]]:
        raise NotImplementedError


class WeekTimeRange(TimeRangeQuery):
    @property
    def query(self) -> Q:
        return Q(datetime__gte=self.now - timedelta(self.now.weekday()))

    def fill_data(
        self, summary: QuerySet, key: str, value: str
    ) -> Tuple[List[float], List[float]]:
        print(summary)
        x = list(range(1, 8))
        y = [0 for i in x]
        for data in summary:
            y[data[key]] = data[value]
        return x, y


class MonthTimeRange(TimeRangeQuery):
    @property
    def query(self) -> Q:
        return Q(datetime__gte=self.now - timedelta(self.now.day - 1))

    def fill_data(
        self, summary: QuerySet, key: str, value: str
    ) -> Tuple[List[float], List[float]]:
        max_day = calendar.monthrange(self.now.year, self.now.month)[1]
        x = list(range(1, max_day + 1))
        y = [0 for i in x]
        for data in summary:
            y[data[key]] = data[value]
        return x, y
