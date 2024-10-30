import numpy as np
import pandas as pd

import ruptures as rpt


class ChangePointDetection:
    """
    Class for detecting change points in a time series.

    Attributes:
        series (pd.Series): Time series data.
        n (int): Length of the time series.
        window_size (float): Window size for change point detection.
        detector (rpt.Pelt): Change point detection object.
        change_points (dict): Dictionary to store detected change points.
    """

    PENALTY = 10
    METHOD = 'PELT'

    def __init__(self, series: pd.Series):
        """
        Initializes the ChangePointDetection with the given time series data.

        Args:
            series (pd.Series): Time series data.
        """

        self.series = series
        self.n = series.__len__()
        self.window_size = np.sqrt(self.n)

        self.detector = rpt.Pelt(model="rbf")
        self.change_points = {}

    def detect_changes(self):
        """
        Detects change points in the time series data using the PELT method.

        The detected change points are stored in the change_points attribute.
        """

        self.detector.fit(self.series.values)

        cp = self.detector.predict(pen=self.PENALTY)
        cp = [x for x in cp if x != self.n]

        if len(cp) > 0:
            self.change_points[self.METHOD] = cp
