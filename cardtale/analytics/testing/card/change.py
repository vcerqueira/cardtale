import pandas as pd
from scipy.stats import ks_2samp
from statsforecast import StatsForecast
from statsforecast.models import ARIMA

from cardtale.analytics.operations.tsa.change_points import ChangePointDetection
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.core.config.analysis import ALPHA
from cardtale.core.data import TimeSeriesData
from cardtale.core.utils.splits import DataSplit

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
        self.change_in_distr = False
        self.distr = {'before': None, 'after': None}

    def run_misc(self, *args, **kwargs):
        """
        Detects change points in the time series data.
        """

        self.detection.detect_changes()
        if len(self.detection.change_points) > 0:
            self.detected_change = True

            self.change_in_distr = self.change_significance(self.series)

            cp, _ = self.get_change_points()
            print('cp')
            print(cp)

            before, after = DataSplit.change_partition(self.series, cp[0], return_data=True)
            # dist_bf, dist_af = KolmogorovSmirnov.best_dist_in_two_parts(before, after)
            # self.distr['before'], self.distr['after'] = dist_bf, dist_af

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

    def run_statistical_tests(self):
        pass

    def run_landmarks(self):
        pass

    @staticmethod
    def get_arima_residuals(data: pd.DataFrame, freq: str, freq_int: int, order=(2, 0, 2)):
        sf = StatsForecast(
            models=[ARIMA(order, season_length=freq_int)],
            freq=freq
        )

        sf.fit(data)
        sf.forecast(fitted=True, h=1)
        insample = sf.forecast_fitted_values().set_index('ds')

        resid = insample['ARIMA'] - insample['y']

        return resid
