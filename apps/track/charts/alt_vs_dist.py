from .base import BaseChart


class AltVSDistChart(BaseChart):
    name = "Altitude"
    x_title = "Distance (km)"
    x_data_method = "dist"
    y_title = "Altitude (m)"
    y_data_method = "alt"
    y_smoother = 30
