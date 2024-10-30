from typing import Tuple, Dict

import pandas as pd

from cardtale.cards.strings import join_l, gettext


# from cardtale.core.utils.errors import AnalysisLogicalError


class SeasonalityTestsParser:
    """
    Class for parsing seasonality test results and generating analysis text.

    Methods:
        seasonal_tests_parser(tests: pd.Series, named_frequency: str) -> str:
            Parses the results of seasonality tests and generates analysis text.
        seasonal_subseries_parser(show_plots: Dict, st_freq: str, lm_freq: str) -> str:
            Parses the results of subseries seasonality tests and generates analysis text.
        subseries_tests_parser(period_name: str, group_trend: pd.Series, overall_level_status: str) -> str:
            Parses the results of subseries tests and generates analysis text.
        get_show_analysis(tests) -> Tuple[Dict, Dict]:
            Determines which plots to show based on seasonality test results.
        show_summary_plot(tester) -> bool:
            Determines whether to show a summary plot based on seasonality test results.
        show_subseries(tester) -> Tuple[bool, Dict]:
            Determines whether to show a subseries plot based on seasonality test results.
    """

    @staticmethod
    def seasonal_tests_parser(tests: pd.Series, named_frequency: str):
        """
        Parses the results of seasonality tests and generates analysis text.

        Args:
            tests (pd.Series): Series containing the results of seasonality tests.
            named_frequency (str): Named frequency for the tests (e.g., 'Monthly').

        Returns:
            str: Analysis text based on the test results.
        """


        all_tests = tests.index.tolist()
        rej_tests = tests[tests > 0].index.tolist()
        not_rej_tests = tests[tests < 1].index.tolist()

        if all(tests > 0):
            analysis_text = gettext('seasonality_line_analysis_seas_all1')
            analysis_text = analysis_text.format(join_l(all_tests), named_frequency)
        elif all(tests < 1):
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
        Parses the results of subseries seasonality tests and generates analysis text.

        Args:
            show_plots (Dict): Dictionary containing the results of subseries tests.
            st_freq (str): Named frequency for statistical tests (e.g., 'Quarterly').
            lm_freq (str): Named frequency for landmark tests (e.g., 'Quarterly').

        Returns:
            str: Analysis text based on the subseries test results.
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
    def subseries_tests_parser(period_name: str,
                               group_trend: pd.Series,
                               overall_level_status: str):
        """
        Parses the results of subseries tests and generates analysis text.

        Args:
            period_name (str): Period name (e.g., 'Month').
            group_trend (pd.Series): Series containing trend probabilities within groups.
            overall_level_status (str): Overall stationarity condition of the time series.

        Returns:
            str: Analysis text based on the subseries test results.
        """

        # data_groups = ds.get_period_groups('Month')
        # overall_level_status = ds.tests.trend.prob_level_str
        if overall_level_status == 'no evidence':
            preprend = 'But, within'
            emphasis = ''
        else:
            preprend = 'Within'
            emphasis = ' also'

        perc_within = 100 * (group_trend > 0.6).mean()
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
            'seas_subseries': [k for k in show_plots
                               if not show_plots[k]['seas_subseries']['show']],
            'seas_summary': [k for k in show_plots
                             if not show_plots[k]['seas_summary']['show']],
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
