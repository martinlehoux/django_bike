from .base import BaseChart, go, smoother


class AltVSDistChart(BaseChart):
    x_title = "Distance (km)"
    y_title = "Altitude (m)"

    def get_data(self):
        x = self.data.dist()
        y1 = smoother(self.data.alt(), 30)
        y2 = smoother(self.data.alt_cum(), 30)
        return [
            go.Scatter(x=x, y=y1, mode="lines", name="Altitude"),
            go.Scatter(x=x, y=y2, mode="lines", name="Positive elevation"),
        ]
