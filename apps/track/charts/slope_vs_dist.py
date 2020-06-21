from .base import BaseChart


class SlopeVSDistChart(BaseChart):
    name = "Slope"
    x_title = "Distance (km)"
    x_data_method = "dist"
    y_title = "Slope (%)"
    y_data_method = "slope"
    y_smoother = 30
