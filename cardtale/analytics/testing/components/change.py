import pandas as pd
from scipy.stats import ks_2samp

from cardtale.analytics.tsa.change import ChangeDetection
from cardtale.analytics.testing.components.base import Tester
from cardtale.data.config.methods import CHANGE_METHOD
from cardtale.data.config.analysis import ALPHA

NO_CHANGE_ERROR = 'No change point has been detected'


class ChangeTesting(Tester):

    def __init__(self, series: pd.Series):
        super().__init__(series)

        self.detected_change = False
        self.method = CHANGE_METHOD
        self.detection = ChangeDetection(series)

    def run_misc(self):
        self.detection.detect_changes()
        if len(self.detection.change_points) > 0:
            self.detected_change = True

    def get_change_points(self):
        if not self.detected_change:
            return [], []

        cp = self.detection.change_points[self.method]

        cp_idx = [x.cp_index for x in cp]

        return cp, cp_idx

    def change_significance(self, series: pd.Series):
        cp, cp_idx = self.get_change_points()

        before = series.values[:cp_idx[0]]
        after = series.values[cp_idx[0]:]

        _, change_p_value = ks_2samp(before, after)
        change_in_dist = change_p_value < ALPHA

        return change_in_dist
