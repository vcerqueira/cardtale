import re
from typing import Tuple, Dict

import numpy as np
import pandas as pd

from cardtale.analytics.operations.tsa.ndiffs import DifferencingTests
from cardtale.analytics.operations.tsa.group_tests import GroupMoments
from cardtale.analytics.operations.landmarking.seasonality import SeasonalLandmarks
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.analytics.testing.card.trend import UnivariateTrendTesting
from cardtale.cards.strings import join_l, gettext
from cardtale.core.config.analysis import ALPHA
from cardtale.core.data import TimeSeriesData

MEANS = 'eq_means'
SDEVS = 'eq_std'


class SeasonalityTesting(UnivariateTester):
    """
    todo o periodo deveria ser parametrizado


    """

    def __init__(self, tsd: TimeSeriesData, freq_naming: str):
        super().__init__(tsd)

        self.period = tsd.period if tsd.period != 1 else None
        self.prob_seasonality = -1
        self.moments = {}
        self.moments_bool = {}
        self.freq_naming = freq_naming

    def run_statistical_tests(self):
        for k, name in DifferencingTests.NSDIFF_TESTS.items():
            if self.period is not None:
                self.tests[name] = \
                    DifferencingTests.nsdiffs(series=self.series,
                                              period=self.period,
                                              test=k)
            else:
                self.tests[name] = np.nan

        self.tests = pd.Series(self.tests)

        self.prob_seasonality = self.tests.mean()

    def run_landmarks(self):
        # adicionar info do period
        seasonal_lm = SeasonalLandmarks(tsd=self.tsd)
        seasonal_lm.run()

        self.performance = seasonal_lm.results

    def run_misc(self):
        freq = re.sub('ly$', '', self.freq_naming)

        data_group = self.tsd.seas_df.groupby(freq, observed=False)[self.tsd.target_col]
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
        self.tests = {}
        self.period_tests = None
        self.summary = None
        self.group_var = []
        # todo to dict for other granularities
        self.seasonal_periods = ['Monthly', 'Quarterly']

        # from pprint import pprint
        # pprint(tcard.tests.seasonality.tests)
        # pd.set_option('display.max_columns', None)
        # tcard.tsd.dt.formats

        self.show_plots = {}
        self.failed_periods = {}

    def run_tests(self):
        self.period_tests = SeasonalityTesting(tsd=self.tsd, freq_naming='')
        self.period_tests.run_statistical_tests()

        freq_df = self.tsd.dt.formats
        freq_df = freq_df[~freq_df['name'].duplicated(), :]

        for _, freq in freq_df.iterrows():
            freq_tests = SeasonalityTesting(tsd=self.tsd, freq_naming=freq['name'])

            freq_tests.run_statistical_tests()
            freq_tests.run_landmarks()
            freq_tests.run_misc()

            if freq_tests.moments_bool['eq_std']:
                if freq['name'] in self.seasonal_periods:
                    self.group_var.append(freq['name'])

            self.tests[freq['name']] = freq_tests

        # summary_df = {}
        # for freq in self.tests:
        #     perf = self.tests[freq].performance
        #     summary_df[freq] = {
        #         'perf_delta': perf['base'] - perf['both'],
        #         'prob': self.tests[freq].prob_seasonality,
        #     }
        #
        # # fixme can I discard this shit table?
        # self.summary = pd.DataFrame(summary_df).T
        # self.summary = self.summary.sort_values(['perf_delta', 'prob'], ascending=False)

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
