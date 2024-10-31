from typing import Tuple, Dict

import numpy as np
import pandas as pd

from cardtale.analytics.operations.tsa.ndiffs import DifferencingTests
from cardtale.analytics.operations.tsa.group_tests import GroupBasedTesting
from cardtale.analytics.operations.landmarking.seasonality import SeasonalLandmarks
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.analytics.testing.card.trend import UnivariateTrendTesting
from cardtale.core.config.analysis import ALPHA
from cardtale.core.data import TimeSeriesData

from cardtale.core.config.freq import PLOTTING_SEAS_CONFIGS


class SeasonalityTesting(UnivariateTester):
    """
    Class for analyzing seasonality in a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        period_data (Dict): Dictionary containing period data for seasonality analysis.
        prob_seasonality (float): Probability of seasonality.
        group_tests (dict): Results of group-based tests.
        group_tests_b (dict): Boolean results of group-based tests.
    """

    def __init__(self,
                 tsd: TimeSeriesData,
                 period_data: Dict):
        """
        Initializes the SeasonalityTesting with the given time series data and period data.

        Args:
            tsd (TimeSeriesData): Time series data object.
            period_data (Dict): Dictionary containing period data for seasonality analysis.
        """

        super().__init__(tsd)

        self.period_data = period_data
        self.prob_seasonality = -1
        self.group_tests = {}
        self.group_tests_b = {}

    def run_statistical_tests(self):
        """
        Runs statistical tests for seasonality.

        Uses the DifferencingTests class to perform non-seasonal differencing tests.
        """

        for k, name in DifferencingTests.NSDIFF_TESTS.items():
            if self.period_data['period'] is not None:
                self.tests[name] = \
                    DifferencingTests.nsdiffs(series=self.series,
                                              period=self.period_data['period'],
                                              test=k)
            else:
                self.tests[name] = np.nan

        self.tests = pd.Series(self.tests)

        self.prob_seasonality = self.tests.mean()

    def run_landmarks(self):
        """
        Runs landmark experiments for seasonality.

        Uses the SeasonalLandmarks class to perform landmark analysis.
        """

        if self.period_data['period'] is None:
            self.performance = {'base': 0, 'both': 0}
            return

        seasonal_lm = SeasonalLandmarks(tsd=self.tsd, target_period=self.period_data['period'])
        seasonal_lm.run()

        self.performance = seasonal_lm.results

    def run_misc(self, *args, **kwargs):
        """
        Runs miscellaneous experiments for seasonality.

        Uses the GroupBasedTesting class to perform group-based tests.
        """

        freq = self.period_data['base']

        data_group = self.tsd.seas_df.groupby(freq, observed=False)[self.tsd.target_col]
        data_group_list = [x.values for _, x in data_group]

        self.group_tests = GroupBasedTesting.run_tests(data_group_list)
        self.group_tests_b = {k: v < ALPHA
                              for k, v in self.group_tests.items()}


class SeasonalityTestingMulti:
    """
    Class for running multiple seasonality tests on a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        period_data_l (list): List of period data configurations for seasonality analysis.
        tests (list): List of SeasonalityTesting objects for each period.
        seas_tests_on_main (pd.Series): Seasonality tests on the main period.
        groups_with_diff_var (list): List of groups with different variance.
        group_trends (dict): Dictionary of group trends.
        show_plots (dict): Dictionary indicating which plots to show.
        failed_periods (dict): Dictionary of failed periods.
    """

    def __init__(self, tsd: TimeSeriesData):
        """
        Initializes the SeasonalityTestingMulti with the given time series data.

        Args:
            tsd (TimeSeriesData): Time series data object.
        """

        self.tsd = tsd

        self.period_data_l = PLOTTING_SEAS_CONFIGS[self.tsd.dt.freq_long.lower()]

        self.tests = []
        self.seas_tests_on_main = None
        self.groups_with_diff_var = []
        self.group_trends = {}

        self.show_plots = {}
        self.failed_periods = {}

    def run_tests(self):
        for period_ in self.period_data_l:
            print(period_)

            seas_tests = SeasonalityTesting(tsd=self.tsd, period_data=period_)
            seas_tests.run_statistical_tests()
            seas_tests.run_landmarks()
            seas_tests.run_misc()

            if period_['main']:
                self.seas_tests_on_main = seas_tests.tests

            if period_['group_tests']:
                # this info will be used in the variance card
                if seas_tests.group_tests_b['eq_std']:
                    self.groups_with_diff_var.append(period_['name'])

                self.group_trends[period_['name']] = self.get_period_groups_trend(period_['name'])

            self.tests.append(seas_tests)

        self.show_plots, self.failed_periods = SeasonalityTestsParser.get_show_analysis(tests=self.tests)

    def get_period_groups_trend(self, period_name: str):
        """
        Gets the trend analysis for each group within the specified period.

        Args:
            period_name (str): Name of the period.

        Returns:
            pd.Series: Series containing the trend probabilities within groups.
        """

        data_groups = self.tsd.get_period_groups(grouping_period=period_name)

        within_group_analysis = {}
        for k, sub_series in data_groups.items():
            # todo fix hardcoded value
            if len(sub_series) < 30:
                prob_level = 0
            else:
                _, prob_level = UnivariateTrendTesting.run_tests_on_series(pd.Series(sub_series))

            within_group_analysis[k] = prob_level

        within_group_analysis_s = pd.Series(within_group_analysis)

        return within_group_analysis_s

    def get_tests_by_named_seasonality(self, named_seasonality: str):
        """
        Gets the SeasonalityTesting object by named seasonality.

        Args:
            named_seasonality (str): Name of the seasonal pattern (e.g., 'Yearly').

        Returns:
            SeasonalityTesting: SeasonalityTesting object for the specified named seasonality.
        """

        for t in self.tests:
            if t.period_data['name'] == named_seasonality:
                return t

        return None


class SeasonalityTestsParser:
    """
    Class for parsing seasonality test results and generating analysis text.

    Methods:
        get_show_analysis(tests) -> Tuple[Dict, Dict]:
            Determines which plots to show based on seasonality test results.
        show_summary_plot(tester) -> bool:
            Determines whether to show a summary plot based on seasonality test results.
        show_subseries(tester) -> Tuple[bool, Dict]:
            Determines whether to show a subseries plot based on seasonality test results.
    """

    @classmethod
    def get_show_analysis(cls, tests):
        """
        Determines which plots to show based on seasonality test results.

        Args:
            tests: SeasonalityTestingMulti.tests object containing the test results.

        Returns:
            Tuple[Dict, Dict]: Dictionary indicating which plots to show and dictionary of failed periods.
        """
        # if len(self.show_plots) > 0:
        #     # analysis was already done
        #     return self.show_plots, self.failed_periods

        show_plots, failed_periods = {}, {}

        for period_tests in tests:
            show_ss, ss_partial_outcomes = cls.show_subseries(period_tests)
            show_summary = cls.show_summary_plot(period_tests)

            show_plots[period_tests.period_data['name']] = {
                'seas_subseries': {
                    'show': show_ss,
                    'which': ss_partial_outcomes,
                },
                'seas_summary': {
                    'show': show_summary,
                }
            }

        failed_periods = {
            'seas_subseries': [k for k, v in show_plots.items()
                               if not v['seas_subseries']['show']],
            'seas_summary': [k for k, v in show_plots.items()
                             if not v['seas_summary']['show']],
        }

        return show_plots, failed_periods

    @staticmethod
    def show_summary_plot(tester) -> bool:
        """
        Determines whether to show a summary plot based on seasonality test results.

        Args:
            tester: SeasonalityTesting object containing the test results.

        Returns:
            bool: Flag indicating whether to show the summary plot.
        """
        grp_tests = tester.group_tests_b

        show_plots_if = grp_tests['eq_means'] or grp_tests['eq_std']

        return show_plots_if

    @staticmethod
    def show_subseries(tester) -> Tuple[bool, Dict]:
        """
        Determines whether to show a subseries plot based on seasonality test results.

        Args:
            tester: SeasonalityTesting object containing the test results.

        Returns:
            Tuple[bool, Dict]: Flag indicating whether to show the subseries plot and dictionary of results.
        """
        period_tests = tester.tests

        any_st_tests_rejects = any(period_tests > 0)
        performance_improves = tester.performance['base'] > tester.performance['both']

        show_results = {
            'by_st': any_st_tests_rejects,
            'by_perf': performance_improves,
        }

        show_me = any_st_tests_rejects or performance_improves

        return show_me, show_results
