import pandas as pd
from scipy.stats import ks_2samp

from cardtale.analytics.operations.tsa.change_points import ChangePointDetection
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.core.config.analysis import ALPHA
from cardtale.core.data import TimeSeriesData

NO_CHANGE_ERROR = 'No change point has been detected'


class ChangeTesting(UnivariateTester):
    """
    Class for detecting and analyzing change points in a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        detected_change (bool): Flag indicating if a change point was detected.
        method (str): Method used for change point detection.
        detection (ChangePointDetection): Change point detection object.
        level_increased (bool): Flag indicating if the level increased after the change point.
    """

    def __init__(self, tsd: TimeSeriesData):
        """
        Initializes the ChangeTesting with the given time series data.

        Args:
            tsd (TimeSeriesData): Time series data object.
        """

        super().__init__(tsd)

        self.detected_change = False
        self.method = ChangePointDetection.METHOD
        self.detection = ChangePointDetection(self.series)
        self.level_increased = False

    def run_misc(self, *args, **kwargs):
        """
        Detects change points in the time series data.
        """

        self.detection.detect_changes()
        if len(self.detection.change_points) > 0:
            self.detected_change = True

    def get_change_points(self):
        """
        Gets the detected change points and their corresponding time steps.

        Returns:
            Tuple[List[int], List[datetime]]: List of change points and list of corresponding time steps.
        """

        if not self.detected_change:
            return [], []

        cp = self.detection.change_points[self.method]

        cp_timestep = [self.series.index[x] for x in cp]

        return cp, cp_timestep

    def change_significance(self, series: pd.Series):
        """
        Determines the significance of the change in the series.

        Args:
            series (pd.Series): Series to analyze for change significance.

        Returns:
            bool: Flag indicating if there is a significant change in distribution.
        """

        cp, _ = self.get_change_points()

        before = series.values[:cp[0]]
        after = series.values[cp[0]:]

        if after.mean() > before.mean():
            self.level_increased = True

        _, change_p_value = ks_2samp(before, after)
        change_in_dist = change_p_value < ALPHA

        return change_in_dist
