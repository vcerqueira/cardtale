from typing import Tuple, Dict

import numpy as np
import pandas as pd

from cardtale.analytics.operations.tsa.ndiffs import DifferencingTests
from cardtale.analytics.operations.tsa.group_tests import GroupBasedTesting
from cardtale.analytics.operations.landmarking.seasonality import SeasonalLandmarks
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.analytics.testing.card.trend import UnivariateTrendTesting
from cardtale.cards.strings import join_l, gettext
from cardtale.core.config.analysis import ALPHA
from cardtale.core.data import TimeSeriesData

from cardtale.core.utils.errors import AnalysisLogicalError
from cardtale.core.config.freq import PLOTTING_SEAS_CONFIGS


class SeasonalityTesting(UnivariateTester):

    def __init__(self,
                 tsd: TimeSeriesData,
                 period_data: Dict):

        super().__init__(tsd)

        self.period_data = period_data
        self.prob_seasonality = -1
        self.group_tests = {}
        self.group_tests_b = {}

    def run_statistical_tests(self):
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
        if self.period_data['period'] is None:
            self.performance = {'base': 0, 'both': 0}
            return

        seasonal_lm = SeasonalLandmarks(tsd=self.tsd, target_period=self.period_data['period'])
        seasonal_lm.run()

        self.performance = seasonal_lm.results

    def run_misc(self):
        freq = self.period_data['base']

        data_group = self.tsd.seas_df.groupby(freq, observed=False)[self.tsd.target_col]
        data_group_list = [x.values for _, x in data_group]

        self.group_tests = GroupBasedTesting.run_tests(data_group_list)
        self.group_tests_b = {k: self.group_tests[k] < ALPHA for k in self.group_tests}


class SeasonalityTestingMulti:

    def __init__(self, tsd: TimeSeriesData):

        self.tsd = tsd

        self.period_data_l = PLOTTING_SEAS_CONFIGS[self.tsd.dt.freq_name.lower()]

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

    def get_period_groups_trend(self, period_name: str):
        # period trends
        data_groups = self.tsd.get_period_groups(grouping_period=period_name)

        within_group_analysis = {}
        for k, sub_series in data_groups.items():
            # todo fix hardcoded value
            if len(sub_series) < 30:
                prob_level = 0
            else:
                prob_trend, prob_level = UnivariateTrendTesting.run_tests_on_series(pd.Series(sub_series))

            within_group_analysis[k] = prob_level

        within_group_analysis_s = pd.Series(within_group_analysis)

        return within_group_analysis_s

    def get_tests_by_named_seasonality(self, named_seasonality: str):
        """
        Get SeasonalityTesting object by named seasonality

        Args:
            named_seasonality:  the name of the seasonal patterns, e.g.
            yaerly seasonality for monthly data when the period is 12

        Returns:

        """
        for t in self.tests:
            if t.period_data['name'] == named_seasonality:
                return t

        return None

