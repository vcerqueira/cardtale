from typing import Dict

import numpy as np
import pandas as pd

from cardtale.analytics.operations.tsa.ndiffs import DifferencingTests
from cardtale.analytics.operations.tsa.group_tests import GroupBasedTesting
from cardtale.analytics.operations.landmarking.seasonality import SeasonalLandmarks
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.analytics.testing.card.trend import UnivariateTrendTesting
from cardtale.analytics.operations.tsa.decomposition import DecompositionSTL
from cardtale.core.data import TimeSeriesData

from cardtale.core.config.freq import PLOTTING_SEAS_CONFIGS


class SeasonalityTesting(UnivariateTester):
    """
    Class for analyzing seasonality in a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        period_data (Dict): Dictionary containing period data for seasonality analysis.
        prob_seasonality (float): Probability of seasonality.
        group_tests (dict): Boolean results of group-based tests.
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
        self.metadata = {}

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
            self.performance = {}
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
        self.metadata['show_summary_plot'] = self._show_summary_plot()

    def _show_summary_plot(self):

        show_plots_if = not (self.group_tests['means_are_eq'] and self.group_tests['var_is_eq'])

        return show_plots_if

    def set_show_subseries_plot(self):
        any_st_tests_rejects = any(self.tests > 0)

        if len(self.performance) > 0:
            perf_improve = pd.Series({
                'fourier': self.performance['base'] > self.performance['fourier'],
                'seas_diffs': self.performance['base'] > self.performance['seas_diffs'],
                'time_features': self.performance['base'] > self.performance['time_features'],
            })
        else:
            perf_improve = pd.Series()

        self.metadata['show_subseries_plot'] = any_st_tests_rejects or perf_improve.any()


class SeasonalityTestingMulti:
    """
    Class for running multiple seasonality tests on a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        period_data_l (list): List of period data configurations for seasonality analysis.
        tests (list): List of SeasonalityTesting objects for each period.
        seas_tests_on_main (pd.Series): Seasonality tests on the main period.
        group_vars (Dict): Dict of groups with variance results.
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

        self.period_data_l = PLOTTING_SEAS_CONFIGS[self.tsd.dt.freq_longly.lower()]

        self.tests = {}
        self.seas_tests_on_main = None
        self.group_vars = {}
        self.group_trends = {}

        self.failed_periods = {
            'seas_subseries': [],
            'seas_summary': [],
        }

        self.seasonal_strength = -1

    def run_tests(self):
        for period_data in self.period_data_l:
            seas_tests = SeasonalityTesting(tsd=self.tsd, period_data=period_data)
            seas_tests.run_statistical_tests()
            seas_tests.run_landmarks()
            seas_tests.run_misc()
            seas_tests.set_show_subseries_plot()

            if period_data['main']:
                self.seas_tests_on_main = seas_tests.tests

            if period_data['group_tests']:
                self.group_trends[period_data['name']] = self.get_period_groups_trend(period_data['name'])
                self.group_vars[period_data['name']] = seas_tests.group_tests['var_is_eq']

            self.tests[period_data['name']] = seas_tests
            self.tests[period_data['name']].metadata = {**self.tests[period_data['name']].metadata, **period_data}

            if not self.tests[period_data['name']].metadata['show_summary_plot']:
                self.failed_periods['seas_summary'].append(period_data['name'])

            if not self.tests[period_data['name']].metadata['show_subseries_plot']:
                self.failed_periods['seas_subseries'].append(period_data['name'])

    def run_misc(self):
        self.seasonal_strength = DecompositionSTL.seasonal_strength(self.tsd.stl_df['Seasonal'],
                                                                    self.tsd.stl_df['Residuals'])

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
