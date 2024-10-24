import numpy as np
import pandas as pd

import ruptures as rpt


class ChangePointDetection:
    PENALTY = 10
    METHOD = 'PELT'

    def __init__(self, series: pd.Series):
        self.series = series
        self.n = series.__len__()
        self.window_size = np.sqrt(self.n)

        self.detector = rpt.Pelt(model="rbf")
        self.change_points = {}

    def detect_changes(self):
        self.detector.fit(self.series.values)

        cp = self.detector.predict(pen=self.PENALTY)
        cp = [x for x in cp if x != self.n]

        if len(cp) > 0:
            self.change_points[self.METHOD] = cp
