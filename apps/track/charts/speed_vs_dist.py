from .base import BaseChart


class SpeedVSDistChart(BaseChart):
    name = "Speed"
    x_title = "Distance (km)"
    x_data_method = "dist"
    y_title = "Speed (km/h)"
    y_data_method = "speed"
    y_smoother = 30
