from typing import Tuple, Dict

import pandas as pd

from cardtale.analytics.operations.landmarking.trend import TrendLandmarks
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.analytics.operations.tsa.ndiffs import DifferencingTests
from cardtale.analytics.operations.tsa.time_model import TimeLinearModel
from cardtale.core.data import TimeSeriesData

TREND_T = 'trend'
LEVEL_T = 'level'


class UnivariateTrendTesting(UnivariateTester):
    """
    Class for running univariate trend tests on time series data.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        tests (dict): Dictionary containing trend and level test results.
        prob_trend (float): Probability of trend.
        prob_level (float): Probability of level.
        time_model (TimeLinearModel): Time linear model for trend analysis.
    """

    def __init__(self, tsd: TimeSeriesData):
        """
        Initializes the UnivariateTrendTesting with the given time series data.

        Args:
            tsd (TimeSeriesData): Time series data object.
        """
        super().__init__(tsd=tsd)

        self.tests = {TREND_T: pd.Series(dtype=int), LEVEL_T: pd.Series(dtype=int)}
        self.prob_trend = -1
        self.prob_level = -1

        self.time_model = TimeLinearModel()

    def run_statistical_tests(self):
        """
        Runs statistical tests for trend and level.

        Uses the DifferencingTests class to perform differencing tests.
        """

        for k, name in DifferencingTests.NDIFF_TESTS.items():
            try:
                for test_type in [TREND_T, LEVEL_T]:
                    self.tests[test_type][name] = \
                        DifferencingTests.ndiffs(series=self.series,
                                                 test=k,
                                                 test_type=test_type)
            except ValueError:
                continue

        self.prob_trend = self.tests[TREND_T].mean()
        self.prob_level = self.tests[LEVEL_T].mean()

    def run_landmarks(self):
        """
        Runs landmark experiments for trend.

        Uses the TrendLandmarks class to perform landmark analysis.
        """

        trend_lm = TrendLandmarks(tsd=self.tsd)
        trend_lm.run()

        self.performance = trend_lm.results

    def run_misc(self, *args, **kwargs):
        self.time_model.fit(self.series)

    def results_in_list(self):
        """
        Returns the results of the trend and level tests as lists.

        Returns:
            Tuple[List[str], List[str], List[str], List[str]]: Lists of trend, no trend, level, and no level results.
        """

        trend_t = self.tests[TREND_T]
        level_t = self.tests[LEVEL_T]

        no_trend = trend_t[trend_t == 0].index.tolist()
        trend = trend_t[trend_t == 1].index.tolist()
        no_level = level_t[level_t == 0].index.tolist()
        level = level_t[level_t == 1].index.tolist()

        return trend, no_trend, level, no_level

    @staticmethod
    def run_tests_on_series(series: pd.Series):
        """
        Runs trend and level tests on a given series.

        Args:
            series (pd.Series): Series to analyze.

        Returns:
            Tuple[float, float]: Probability of trend and probability of level.
        """

        # series = pd.Series([2640,5640, 2160,3600,2640,4680])

        tests = {TREND_T: pd.Series(dtype=int), LEVEL_T: pd.Series(dtype=int)}

        for k, name in DifferencingTests.NDIFF_TESTS.items():
            for test_type in [TREND_T, LEVEL_T]:
                tests[test_type][name] = DifferencingTests.ndiffs(series=series, test=k, test_type=test_type)

        prob_trend = tests[TREND_T].mean()
        prob_level = tests[LEVEL_T].mean()

        return prob_trend, prob_level


class TrendTestsParser:
    """
    Class for parsing trend test results and generating analysis text.

    Methods:
        show_trend_plots(tester: UnivariateTrendTesting) -> Tuple[bool, Dict]:
            Determines which trend plots to show based on test results.
    """

    @staticmethod
    def show_trend_plots(tester: UnivariateTrendTesting) -> Tuple[bool, Dict]:
        """
        Determines which trend plots to show based on test results.

        Args:
            tester (UnivariateTrendTesting): Object containing the trend test results.

        Returns:
            Tuple[bool, Dict]: Flag indicating whether to show the trend plots and dictionary of results.
        """

        perf = tester.performance

        diff_improves = perf['base'] > perf['first_differences']
        t_improves = perf['base'] > perf['trend_feature']

        show_results = {
            'by_trend': tester.prob_trend > 0,
            'by_level': tester.prob_level > 0,
            'by_diff': diff_improves,
            'by_t': t_improves,
        }

        show_me = any([*show_results.values()])

        return show_me, show_results
