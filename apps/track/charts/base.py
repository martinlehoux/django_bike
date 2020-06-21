from plotly.offline import plot
from plotly import graph_objs as go

from ..models import Track, TrackData, smoother


class BaseChart:
    track: Track
    data: TrackData
    layout: go.Layout
    figure: go.Figure
    name: str
    x_title: str
    x_data_method: str
    x_smoother: int = 0
    y_title: str
    y_data_method: str
    y_smoother: int = 0

    def __init__(self, track: Track):
        self.track = track
        self.data = TrackData(track)
        self.layout = self.get_layout()
        self.figure = self.get_figure()

    def get_layout(self):
        return go.Layout(
            title=self.track.name,
            xaxis=dict(title=self.x_title),
            yaxis=dict(title=self.y_title),
            margin=dict(r=0, l=0, t=40, b=0),
        )

    def get_figure(self):
        x = getattr(self.data, self.x_data_method)()
        if self.x_smoother:
            x = smoother(x, self.x_smoother)
        y = getattr(self.data, self.y_data_method)()
        if self.y_smoother:
            y = smoother(y, self.y_smoother)
        return go.Figure(
            data=[go.Scatter(x=x, y=y, mode="lines", name=self.name)],
            layout=self.layout,
        )

    def plot(self):
        return plot(self.figure, output_type="div", include_plotlyjs=False)
