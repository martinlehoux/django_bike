from datetime import datetime
from typing import List

from django.utils import timezone
from django.contrib.auth import get_user_model
from plotly.offline import plot
from plotly import graph_objs as go


User = get_user_model()


class BaseChart:
    user: User
    now: datetime
    figure: go.Figure
    name: str
    x_title: str
    y_title: str

    def __init__(self, user: User, now=timezone.now()):
        self.user = user
        self.now = now
        self.figure = self.get_figure()

    def get_layout(self, data):
        y_range = [0, max(max(fig.y) for fig in data) + 5]
        if y_range == [0, 0]:
            y_range = [0, 10]
        return go.Layout(
            title=self.name,
            xaxis=dict(title=self.x_title),
            yaxis=dict(title=self.y_title, range=y_range),
            margin=dict(r=0, l=0, t=40, b=0),
        )

    def get_data(self) -> List:
        raise NotImplementedError()

    def get_figure(self):
        data = self.get_data()
        layout = self.get_layout(data)
        return go.Figure(data=data, layout=layout)

    def plot(self):
        return plot(self.figure, output_type="div", include_plotlyjs=False)
