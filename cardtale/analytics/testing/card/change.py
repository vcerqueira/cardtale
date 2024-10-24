import pandas as pd
from scipy.stats import ks_2samp

from cardtale.analytics.operations.tsa.change import ChangePointDetection
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.core.config.analysis import ALPHA
from cardtale.core.data import TimeSeriesData

NO_CHANGE_ERROR = 'No change point has been detected'


class ChangeTesting(UnivariateTester):

    def __init__(self, tsd: TimeSeriesData):
        super().__init__(tsd)

        self.detected_change = False
        self.method = ChangePointDetection.METHOD
        self.detection = ChangePointDetection(self.series)
        self.level_increased = False

    def run_misc(self):
        self.detection.detect_changes()
        if len(self.detection.change_points) > 0:
            self.detected_change = True

    def get_change_points(self):
        if not self.detected_change:
            return [], []

        cp = self.detection.change_points[self.method]

        cp_timestep = [self.series.index[x] for x in cp]

        return cp, cp_timestep

    def change_significance(self, series: pd.Series):
        cp, cp_timestep = self.get_change_points()

        before = series.values[:cp[0]]
        after = series.values[cp[0]:]

        if after.mean() > before.mean():
            self.level_increased = True

        _, change_p_value = ks_2samp(before, after)
        change_in_dist = change_p_value < ALPHA

        return change_in_dist
