from .base import BaseChart


class PowerVSTimeChart(BaseChart):
    name = "Power"
    x_title = "Dist (km)"  # TODO: Time
    x_data_method = "dist"  # TODO
    y_title = "Power (W)"
    y_data_method = "power"
    y_smoother = 30
