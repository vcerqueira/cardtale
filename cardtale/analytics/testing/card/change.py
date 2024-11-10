import numpy as np
import pandas as pd
from scipy import stats
from statsforecast import StatsForecast
from statsforecast.models import ARIMA

from cardtale.analytics.operations.tsa.change_points import ChangePointDetection
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.analytics.operations.landmarking.change import ChangeLandmarks
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
        self.chow_p_value = -1

    def run_misc(self, *args, **kwargs):
        """
        Detects change points in the time series data.
        """

        self.detection.detect_changes()
        if len(self.detection.change_points) > 0:
            self.detected_change = True

            self.change_in_distr = self.change_significance(self.series)

    def run_statistical_tests(self):
        if len(self.detection.change_points) > 0:
            self.chow_p_value = self.chow_test_on_resid()

    def run_landmarks(self):
        if len(self.detection.change_points) > 0:
            change_lm = ChangeLandmarks(self.tsd, self.detection.change_points[self.method][0])
            change_lm.run()

            self.performance = change_lm.results

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

        _, change_p_value = stats.ks_2samp(before, after)
        change_in_dist = change_p_value < ALPHA

        return change_in_dist

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

        return resid.values

    def chow_test_on_resid(self):
        cp, _ = self.get_change_points()

        assert len(cp) > 0, NO_CHANGE_ERROR

        before, after = DataSplit.change_partition(self.tsd.df, cp[0], return_data=True)

        resid_before = self.get_arima_residuals(before, self.tsd.dt.freq_short, self.tsd.period)
        resid_after = self.get_arima_residuals(after, self.tsd.dt.freq_short, self.tsd.period)
        resid_all = self.get_arima_residuals(self.tsd.df, self.tsd.dt.freq_short, self.tsd.period)
        n_params = 5  # ARIMA(2,0,2)

        p_val = self._chow_test(resid_before, resid_after, resid_all, n_params=n_params)

        return p_val

    @staticmethod
    def _chow_test(resid1: np.ndarray, resid2: np.ndarray, resid_all: np.ndarray, n_params: int):
        rss1 = np.sum(resid1 ** 2)
        rss2 = np.sum(resid2 ** 2)
        rss_r = rss1 + rss2  # Restricted RSS (separate models)
        rss_ur = np.sum(resid_all ** 2)

        # Calculate degrees of freedom
        n1, n2 = len(resid1), len(resid2)

        # Calculate F-statistic
        f_stat = ((rss_ur - rss_r) / n_params) / (rss_r / (n1 + n2 - 2 * n_params))

        # Calculate p-value
        p_value = 1 - stats.f.cdf(f_stat, n_params, n1 + n2 - 2 * n_params)

        return p_value
