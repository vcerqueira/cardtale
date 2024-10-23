from typing import Tuple, Dict

import pandas as pd

from cardtale.analytics.operations.landmarking.trend import TrendLandmarks
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.analytics.operations.tsa.ndiffs import R_NDIFF_TESTS, RNDiffs
from cardtale.analytics.operations.tsa.time_model import TimeLinearModel
from cardtale.cards.strings import gettext
from cardtale.core.data import TimeSeriesData

TREND_T = 'trend'
LEVEL_T = 'level'


class UnivariateTrendTesting(UnivariateTester):

    def __init__(self, tsd: TimeSeriesData):
        """
        todo docs

        """
        super().__init__(tsd=tsd)

        self.tests = {TREND_T: pd.Series(dtype=int),
                      LEVEL_T: pd.Series(dtype=int)}
        self.prob_trend = -1
        self.prob_level = -1
        self.prob_level_str = ''

        self.time_model = TimeLinearModel()

    def run_statistical_tests(self):
        for k, name in R_NDIFF_TESTS.items():
            try:
                for test_type in [TREND_T, LEVEL_T]:
                    self.tests[test_type][name] = RNDiffs.r_ndiffs(self.series, test=k, test_type=test_type)
            except ValueError:
                continue

        self.prob_trend = self.tests[TREND_T].mean()
        self.prob_level = self.tests[LEVEL_T].mean()
        if self.prob_level < 0.3:
            self.prob_level_str = 'no evidence'
        elif self.prob_level < 0.6:
            self.prob_level_str = 'a slight evidence'
        elif self.prob_level < 0.9:
            self.prob_level_str = 'a reasonable evidence'
        else:
            self.prob_level_str = 'a strong evidence'

    def run_landmarks(self):
        trend_lm = TrendLandmarks(tsd=self.tsd)
        trend_lm.run()

        self.performance = trend_lm.results

    def run_misc(self):
        self.time_model.fit(self.series)

    def results_in_list(self):
        trend_t = self.tests[TREND_T]
        level_t = self.tests[LEVEL_T]

        no_trend = trend_t[trend_t == 0].index.tolist()
        trend = trend_t[trend_t == 1].index.tolist()
        no_level = level_t[level_t == 0].index.tolist()
        level = level_t[level_t == 1].index.tolist()

        return trend, no_trend, level, no_level

    def parse_t_performance(self):

        perf = self.performance

        t_improves = perf['base'] > perf['trend_feature']

        if t_improves:
            analysis_text = gettext('trend_line_analysis_t_good')
        else:
            analysis_text = gettext('trend_line_analysis_t_bad')

        return analysis_text

    def parse_differencing_performance(self):

        perf = self.performance

        diff_improves = perf['base'] > perf['first_differences']

        if diff_improves:
            analysis_text = gettext('trend_line_analysis_diff_good')
        else:
            analysis_text = gettext('trend_line_analysis_diff_bad')

        return analysis_text

    @staticmethod
    def run_tests_on_series(series: pd.Series):
        tests = {TREND_T: pd.Series(dtype=int),
                 LEVEL_T: pd.Series(dtype=int)}

        for k, name in R_NDIFF_TESTS.items():
            try:
                for test_type in [TREND_T, LEVEL_T]:
                    tests[test_type][name] = RNDiffs.r_ndiffs(series, test=k, test_type=test_type)
            except ValueError:
                continue

        prob_trend = tests[TREND_T].mean()
        prob_level = tests[LEVEL_T].mean()

        return prob_trend, prob_level


class TrendShowTests:

    @staticmethod
    def show_line_plot(tests: UnivariateTrendTesting) -> Tuple[bool, Dict]:
        """
        todo identical tests for distribution plot. what other tests should I do?
        show_me, show_results = TrendTesting.show_distribution_plot(ds.tests.trend)

        :param tests: TrendTesting object
        """
        is_trend_st = tests.prob_trend > 0
        is_level_st = tests.prob_level > 0

        diff_improves = tests.performance['base'] > tests.performance['first_differences']
        t_improves = tests.performance['base'] > tests.performance['trend_feature']
        # both_improve = tests.performance['base'] > tests.performance['both']

        show_me = is_trend_st or is_level_st or diff_improves or t_improves

        show_results = {
            'by_trend': is_trend_st,
            'by_level': is_level_st,
            'by_diff': diff_improves,
            'by_t': t_improves,
        }

        return show_me, show_results

    @staticmethod
    def show_distribution_plot(tests: UnivariateTrendTesting) -> Tuple[bool, Dict]:
        """
        show_me, show_results = TrendTesting.show_distribution_plot(ds.tests.trend)

        :param tests: TrendTesting object
        """
        is_trend_st = tests.prob_trend > 0
        is_level_st = tests.prob_level > 0

        diff_improves = tests.performance['base'] > tests.performance['first_differences']
        t_improves = tests.performance['base'] > tests.performance['trend_feature']
        # both_improve = tests.performance['base'] > tests.performance['both']

        show_me = is_trend_st or is_level_st or diff_improves or t_improves

        show_results = {
            'by_trend': is_trend_st,
            'by_level': is_level_st,
            'by_diff': diff_improves,
            'by_t': t_improves,
        }

        return show_me, show_results
