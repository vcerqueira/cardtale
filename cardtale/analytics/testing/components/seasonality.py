from pprint import pprint
import re
from typing import Optional, Tuple, Dict

import numpy as np
import pandas as pd

from cardtale.analytics.tsa.ndiffs import RNDiffs, R_NSDIFF_TESTS
from cardtale.analytics.tsa.group_moments import GroupMoments
from cardtale.analytics.testing.landmarking.seasonality import SeasonalLandmarks
from cardtale.analytics.testing.components.base import UnivariateTester
from cardtale.analytics.testing.components.trend import UnivariateTrendTesting
from cardtale.cards.strings import join_l, gettext
from cardtale.core.config.analysis import ALPHA
from cardtale.core.config.typing import Period
from cardtale.core.utils.errors import AnalysisLogicalError, LOGICAL_ERROR_MSG
from cardtale.core.data import TimeSeriesData

MEANS = 'eq_means'
SDEVS = 'eq_std'


class SeasonalityTesting(UnivariateTester):
    """
    todo add estimated cycle to list of plausible cycles
    todo add effect of seasonal differencing -- need to implement inv season diff
    """

    def __init__(self,
                 series: pd.Series,
                 period: Period,
                 named_freq: str):
        super().__init__(series)

        self.period = period if period != 1 else None
        self.named_freq = named_freq
        self.est_period = -1
        self.prob_seasonality = -1
        self.moments = {}
        self.moments_bool = {}

    def run_statistical_tests(self):
        for k, name in R_NSDIFF_TESTS.items():
            if self.period is not None:
                self.tests[name] = RNDiffs.r_nsdiffs(self.series, self.period, k)
            else:
                self.tests[name] = np.nan

        self.tests = pd.Series(self.tests)

        self.prob_seasonality = self.tests.mean()

    def run_landmarks(self):
        seasonal_lm = SeasonalLandmarks(period=self.period)

        seasonal_lm.make_tests(self.series)

        self.performance = seasonal_lm.results

    def run_misc(self, seasonal_df: pd.DataFrame):
        freq = re.sub('ly$', '', self.named_freq)

        data_group = seasonal_df.groupby(freq)[SERIES]
        data_group_list = [x.values for _, x in data_group]

        self.moments = GroupMoments.compare_groups(data_group_list)
        self.moments_bool = {k: self.moments[k] < ALPHA for k in self.moments}

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
        print(st_freq)
        print(lm_freq)
        pprint(show_plots)
        # show_plots = {'Monthly': {'seas_subseries': {'show': False, 'which': {'by_st': False, 'by_perf': False}}, 'seas_summary': {'show': False}}, 'Quarterly': {'seas_subseries': {'show': True, 'which': {'by_st': False, 'by_perf': True}}, 'seas_summary': {'show': False}}, 'Yearly': {'seas_subseries': {'show': True, 'which': {'by_st': False, 'by_perf': True}}, 'seas_summary': {'show': True}}}
        # st_freq='Monthly'
        # lm_freq='Yearly'
        # from pprint import pprint
        # pprint(show_plots)

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
            # raise AnalysisLogicalError(LOGICAL_ERROR_MSG)

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
        for k, sub_series in data_groups.items():
            # print(k)
            trend = TrendTesting(pd.Series(sub_series))
            trend.run_statistical_tests()
            within_group_analysis[k] = trend.prob_level

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

    def __init__(self,
                 series: pd.Series,
                 frequency_df: pd.DataFrame,
                 period: Period):

        self.series = series
        self.frequency_df = frequency_df
        self.period = period
        self.tests = {}
        self.period_tests = None
        self.summary = None
        self.group_var = []
        # todo to dict for other granularities
        self.analysed_periods = ['Monthly', 'Quarterly']

        self.show_plots = {}
        self.failed_periods = {}

    def run_tests(self, seasonal_df: pd.DataFrame):
        self.period_tests = SeasonalityTesting(series=self.series,
                                               period=self.period,
                                               named_freq='',
                                               named_period=None)

        self.period_tests.run_statistical_tests()

        for _, freq in self.frequency_df.iterrows():
            freq_tests = SeasonalityTesting(series=self.series,
                                            period=freq['period'],
                                            named_freq=freq['name'],
                                            named_period=freq['index'])

            freq_tests.run_statistical_tests()
            freq_tests.run_landmarks()
            freq_tests.run_misc(seasonal_df)

            if freq_tests.moments_bool['eq_std']:
                if freq['name'] in self.analysed_periods:
                    self.group_var.append(freq['name'])

            self.tests[freq['name']] = freq_tests

        summary_df = {}
        for freq in self.tests:
            perf = self.tests[freq].performance
            summary_df[freq] = {
                'perf_delta': perf['base'] - perf['both'],
                'prob': self.tests[freq].prob_seasonality,
            }

        # fixme can I discard this shit table?
        self.summary = pd.DataFrame(summary_df).T
        self.summary = self.summary.sort_values(['perf_delta', 'prob'], ascending=False)
        print(self.summary)

    def get_show_analysis(self):
        if len(self.show_plots) > 0:
            # analysis was already done
            return self.show_plots, self.failed_periods

        for k in self.tests:
            show_ss, ss_partial_outcomes = SeasonalityShowTests.show_subseries(self.tests[k])
            show_summary = SeasonalityShowTests.show_summary_plot(self.tests[k])

            self.show_plots[k] = {
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
        group_comps = tests.moments_bool

        rej_mean = group_comps[MEANS]
        rej_std = group_comps[SDEVS]

        show_me = rej_mean or rej_std

        return show_me

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
