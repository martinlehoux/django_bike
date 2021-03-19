from .base import BaseChart, go


class AltVSDistChart(BaseChart):
    x_title = "Distance (km)"
    y_title = "Elevation (m)"

    def get_data(self):
        x = self.data.dist()
        y = self.data.alt()
        return [
            go.Scatter(x=x, y=y, mode="lines", name="Elevation"),
        ]
