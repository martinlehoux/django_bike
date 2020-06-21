from .base import BaseChart, go


class MapChart(BaseChart):
    name = "Track map"
    x_title = "X (m)"
    y_title = "Y (m)"

    def get_figure(self):
        x = self.data.x()
        y = self.data.y()
        z = self.data.alt()
        return go.Figure(
            data=[go.Scatter3d(x=x, y=y, z=z, mode="lines", name=self.name)],
            layout=self.layout,
        )
