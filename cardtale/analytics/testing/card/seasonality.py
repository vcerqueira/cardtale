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

    @staticmethod
    def seasonal_tests_parser(tests_results: pd.Series, named_frequency: str):

        all_tests = tests_results.index.tolist()
        rej_tests = tests_results[tests_results > 0].index.tolist()
        not_rej_tests = tests_results[tests_results < 1].index.tolist()

        if all(tests_results > 0):
            analysis_text = gettext('seasonality_line_analysis_seas_all1')
            analysis_text = analysis_text.format(join_l(all_tests), named_frequency)
        elif all(tests_results < 1):
            analysis_text = gettext('seasonality_line_analysis_seas_all0')
            analysis_text = analysis_text.format(join_l(all_tests), named_frequency)
        else:
            analysis_text = gettext('seasonality_line_analysis_seas_mix')
            analysis_text = analysis_text.format(named_frequency,
                                                 join_l(rej_tests),
                                                 join_l(not_rej_tests))

        return analysis_text

    @staticmethod
    def seasonal_subseries_parser(show_plots: Dict, st_freq: str, lm_freq: str):
        """

        :param show_plots: First element from outcome of SeasonalityTestingMulti.get_show_analysis()
        :param st_freq: Named frequency for statistical tests (e.g. Quarterly)
        :param lm_freq: Named frequency for landmark tests (e.g. Quarterly)

        When do these differ?
        For the main period... For example, suppose the ts is monthly.
        The main period is 12 for yearly seasonality.
        The statistical tests look for a named yearly seasonality,
        but landmarks look for a monthly information...
        What a mess... but I'm not sure how to unshit this.

        :return: text content
        """

        by_st = show_plots[st_freq]['seas_subseries']['which']['by_st']
        by_perf = show_plots[lm_freq]['seas_subseries']['which']['by_perf']

        if not by_st and by_perf:
            effect_analysis = gettext('seasonality_subseries_opt1')
        elif by_st and not by_perf:
            effect_analysis = gettext('seasonality_subseries_opt2')
        elif by_st and by_perf:
            effect_analysis = gettext('seasonality_subseries_opt3')
        else:
            return None
            # todo check this
            # raise AnalysisLogicalError('AnalysisLogicalError---')

        effect_analysis = effect_analysis.format(st_freq.lower())

        return effect_analysis

    @staticmethod
    def seasonal_subseries_st_parser(period_name: str,
                                     data_groups: Dict,
                                     overall_level_status: str):
        """
        :param period_name: Period name (e.g. month)
        :param data_groups: Dict with time series by group
        :param overall_level_status: Overall stationarity condition of the time series
        """
        # data_groups = ds.get_period_groups('Month')
        # overall_level_status = ds.tests.trend.prob_level_str
        if overall_level_status == 'no evidence':
            preprend = 'But, within'
            emphasis = ''
        else:
            preprend = 'Within'
            emphasis = ' also'

        within_group_analysis = {}
        # print('subseries items')
        for k, sub_series in data_groups.items():
            if len(sub_series) < 30:
                prob_level = 0
            else:
                prob_trend, prob_level = UnivariateTrendTesting.run_tests_on_series(pd.Series(sub_series))

            within_group_analysis[k] = prob_level

        print('finished seas')

        within_group_analysis_s = pd.Series(within_group_analysis)
        perc_within = 100 * (within_group_analysis_s > 0.6).mean()
        perc_within_str = f'{int(perc_within)}%'
        if perc_within_str == '100%':
            perc_within_str = 'all'
        elif perc_within_str == '0%':
            perc_within_str = 'none'

        part1 = gettext('seasonality_subseries_group1').format(overall_level_status)
        if overall_level_status == 'no evidence':
            if perc_within_str == 'none':
                part2 = gettext('seasonality_subseries_group2bothnone').format(period_name)
                return f'{part1} {part2}'
        else:
            if perc_within_str == 'none':
                part2 = gettext('seasonality_subseries_group2none').format(period_name)
                return f'{part1} {part2}'

        part2 = gettext('seasonality_subseries_group2')
        part2 = part2.format(preprend, emphasis, perc_within_str, period_name)

        return f'{part1} {part2}'


class SeasonalityTestingMulti:

    def __init__(self, tsd: TimeSeriesData):

        self.tsd = tsd

        self.period_data_l = PLOTTING_SEAS_CONFIGS[self.tsd.dt.freq_name.lower()]

        self.tests = []
        self.seas_tests_on_main = None
        self.groups_with_diff_var = []

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

            if seas_tests.group_tests_b['eq_std']:
                if period_['group_tests']:
                    # this info will be used in the variance card
                    self.groups_with_diff_var.append(period_['name'])

            self.tests.append(seas_tests)

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

    def get_show_analysis(self):
        if len(self.show_plots) > 0:
            # analysis was already done
            return self.show_plots, self.failed_periods

        for period_tests in self.tests:
            show_ss, ss_partial_outcomes = SeasonalityShowTests.show_subseries(period_tests)
            show_summary = SeasonalityShowTests.show_summary_plot(period_tests)

            self.show_plots[period_tests.period_data['name']] = {
                'seas_subseries': {
                    'show': show_ss,
                    'which': ss_partial_outcomes,
                },
                'seas_summary': {
                    'show': show_summary,
                }
            }

        self.failed_periods = {
            'seas_subseries': [k for k in self.show_plots
                               if not self.show_plots[k]['seas_subseries']['show']],
            'seas_summary': [k for k in self.show_plots
                             if not self.show_plots[k]['seas_summary']['show']],
        }

        return self.show_plots, self.failed_periods


class SeasonalityShowTests:

    @staticmethod
    def show_summary_plot(tests: SeasonalityTesting) -> bool:
        grp_tests = tests.group_tests_b

        show_plots_if = grp_tests['eq_means'] or grp_tests['eq_std']

        return show_plots_if

    @staticmethod
    def show_subseries(tests: SeasonalityTesting) -> Tuple[bool, Dict]:
        """
        Testing whether a subseries plot should be shown based on SeasonalityTesting results
        :param tests: SeasonalityTesting object

        :return: bool (whether to show), dict (which component(s) defines result)
        """
        period_tests = tests.tests

        any_st_tests_rejects = any(period_tests > 0)
        performance_improves = tests.performance['base'] > tests.performance['both']

        show_results = {
            'by_st': any_st_tests_rejects,
            'by_perf': performance_improves,
        }

        show_me = any_st_tests_rejects or performance_improves

        return show_me, show_results
