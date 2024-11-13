from typing import Optional

import pandas as pd

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.seasonal import SeasonalPlot

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import PLOT_NAMES
from cardtale.cards.strings import join_l, gettext


class SeasonalSubSeriesPlot(Plot):
    """
    Class for creating and analyzing seasonal subseries plots.

    Attributes:
        tests_were_analysed (bool): Flag indicating if tests were already analyzed.
        caption (str): Caption for the plot.
        x_axis_col (str): Column name for the x-axis.
        y_axis_col (str): Column name for the y-axis.
        named_seasonality (str): Named seasonality for the plot.
        caption_expr (str): Expression for the caption.
        plot_id (str): Identifier for the plot.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for seasonality.
    """

    def __init__(self,
                 tsd: TimeSeriesData,
                 tests: TestingComponents,
                 name: str,
                 named_seasonality: str,
                 x_axis_col: str,
                 y_axis_col: str,
                 tests_were_analysed: bool):
        """
        Initializes the SeasonalSubSeriesPlot class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for seasonality.
            name (str): Name of the plot.
            named_seasonality (str): Named seasonality for the plot.
            x_axis_col (str): Column name for the x-axis.
            y_axis_col (str): Column name for the y-axis.
            tests_were_analysed (bool): Flag indicating if tests were already analyzed.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.tests_were_analysed = tests_were_analysed

        self.caption = gettext('seasonality_subseries_caption')
        self.x_axis_col = x_axis_col
        self.y_axis_col = y_axis_col
        self.named_seasonality = named_seasonality

        self.caption_expr = f'{self.x_axis_col}ly'.lower()

        self.plot_id = 'seas_subseries'

        self.plot_name = PLOT_NAMES[self.plot_id]
        self.plot_name += f' ({self.x_axis_col}ly)'

        self.tests = tests

    def build(self, *args, **kwargs):
        """
        Creates the seasonal subseries plot.
        """

        self.plot = SeasonalPlot.sub_series(data=self.tsd.seas_df,
                                            group_col=self.x_axis_col,
                                            x_axis_col=self.tsd.time_col,
                                            y_axis_col=self.y_axis_col)

    def analyse(self, *args, **kwargs):
        """
        Analyzes the seasonal subseries plot.

        The analysis includes checking for seasonality and summarizing the results.
        """

        if self.tests.seasonality.tests[self.named_seasonality].metadata['show_subseries_plot']:
            self.show_me = True
        else:
            return

        plt_deq1 = self.deq_group_differences_aux()
        plt_deq2 = self.deq_seasonality_stationarity()
        # plt_deq3 = self.deq_seasonality_trend()
        plt_deq4 = self.deq_seasonality_impact()

        self.analysis = [plt_deq1, plt_deq2, plt_deq4]
        # self.analysis = [plt_deq1, plt_deq2, plt_deq3, plt_deq4]
        self.analysis = [x for x in self.analysis if x is not None]

    def format_caption(self, plot_id: int):
        """
        Formats the caption with the respective number and method.

        Args:
            plot_id (int): Plot id.
        """

        self.img_data['caption'] = self.img_data['caption'].format(plot_id, self.caption_expr.title(),
                                                                   self.caption_expr)

    def deq_group_differences_aux(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Are there statistical differences in the time series groups?

        Approach:
            - anova_test
            - kruskal_test
            - levene_test
            - bartlett_test
        """

        freq_longly = 'Daily' if self.x_axis_col == 'Day' else f'{self.x_axis_col}ly'

        tests = self.tests.seasonality.tests[freq_longly]

        if not tests.metadata['show_summary_plot']:
            expr = gettext('seasonality_summary_fail')
            expr_fmt = expr.format(freq_longly=freq_longly.lower(),
                                   freq_long_plural=f'{self.x_axis_col.lower()}s')
        else:
            expr_fmt = None

        return expr_fmt

    def deq_seasonality_stationarity(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Is the time series stationary in seasonality for the given period?

        Approach:
            - Statistical tests
        """

        freq_longly = 'Daily' if self.x_axis_col == 'Day' else f'{self.x_axis_col}ly'

        tests = self.tests.seasonality.tests[self.named_seasonality].tests

        all_tests = tests.index.tolist()
        rej_tests = tests[tests > 0].index.tolist()
        not_rej_tests = tests[tests < 1].index.tolist()

        if self.tests_were_analysed:
            return None

        if all(tests > 0):
            expr = gettext('series_components_analysis_seas_all1')
            expr_fmt = expr.format(join_l(all_tests), freq_longly.lower())
        elif all(tests < 1):
            expr = gettext('series_components_analysis_seas_all0')
            expr_fmt = expr.format(join_l(all_tests), freq_longly.lower())
        else:
            expr = gettext('series_components_analysis_seas_mix')
            conclusion = 'seasonal unit root' if rej_tests[0] == 'OCSB' else 'strong seasonality'
            expr_fmt = expr.format(freq_longly=freq_longly.lower(),
                                   test1=rej_tests[0],
                                   test1_conclusion=conclusion,
                                   test2=not_rej_tests[0])

        return expr_fmt

    def deq_seasonality_trend(self) -> Optional[str]:
        """
        todo this analysis is quite sketchy

        DEQ (Data Exploratory Question): Is there a trend within seasonal periods of the time series?

        Approach:
            - Statistical tests
        """

        freq_longly = 'Daily' if self.x_axis_col == 'Day' else f'{self.x_axis_col}ly'

        if freq_longly not in self.tests.seasonality.group_trends:
            return None

        prob = self.tests.trend.prob_level

        if prob < 0.3:
            named_level_st = 'no evidence'
        elif prob < 0.6:
            named_level_st = 'a slight evidence'
        elif prob < 0.9:
            named_level_st = 'a reasonable evidence'
        else:
            named_level_st = 'a strong evidence'

        g_trend = self.tests.seasonality.group_trends[freq_longly]

        if named_level_st == 'no evidence':
            preprend = 'But, within'
            emphasis = ''
        else:
            preprend = 'Within'
            emphasis = ' also'

        perc_within = 100 * (g_trend > 0.6).mean()
        perc_within_str = f'{int(perc_within)}%'
        if perc_within_str == '100%':
            perc_within_str = 'all'
        elif perc_within_str == '0%':
            perc_within_str = 'none'

        expr_fmt1 = gettext('seasonality_subseries_group1').format(named_level_st)
        if named_level_st == 'no evidence':
            if perc_within_str == 'none':
                expr_fmt2 = gettext('seasonality_subseries_group2bothnone').format(self.x_axis_col)
                expr_fmt = f'{expr_fmt1} {expr_fmt2}'
                return expr_fmt
        else:
            if perc_within_str == 'none':
                expr_fmt2 = gettext('seasonality_subseries_group2none').format(self.x_axis_col)
                expr_fmt = f'{expr_fmt1} {expr_fmt2}'
                return expr_fmt

        expr2 = gettext('seasonality_subseries_group2')
        expr_fmt2 = expr2.format(preprend, emphasis, perc_within_str, self.x_axis_col)

        expr_fmt = f'{expr_fmt1} {expr_fmt2}'

        return expr_fmt

    def deq_seasonality_impact(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Is there a trend within seasonal periods of the time series?

        Approach:
            - Statistical tests
        """

        freq_longly = 'Daily' if self.x_axis_col == 'Day' else f'{self.x_axis_col}ly'

        tests = self.tests.seasonality.tests[freq_longly]

        if len(tests.performance) < 1:
            self.show_me = False
            return None

        perf_improves = min(tests.performance['fourier'],
                            tests.performance['seas_diffs'],
                            tests.performance['time_features']) < tests.performance['base']

        any_test_fails = (tests.tests > 0).any()

        if not any_test_fails and not perf_improves:
            self.show_me = False
            return None

        perf = self.tests.seasonality.tests[freq_longly].performance
        perf = pd.Series(perf).round(2)

        improves = min(perf['fourier'], perf['seas_diffs'], perf['time_features']) < perf['base']

        effect = 'can improve' if improves else 'does not improve'

        if not any_test_fails and perf_improves:
            expr_fmt0 = gettext('seasonality_subseries_st_opt1').format(freq_longly.lower())
        elif any_test_fails and not perf_improves:
            expr_fmt0 = gettext('seasonality_subseries_st_opt2').format(freq_longly.lower())
        else:
            expr_fmt0 = gettext('seasonality_subseries_st_opt3').format(freq_longly.lower())

        expr = gettext('seasonality_subseries')

        expr_fmt = expr.format(tests_result=expr_fmt0,
                               named_frequency=self.named_seasonality.lower(),
                               overall_effect=effect,
                               base=perf['base'],
                               fourier=perf['fourier'],
                               freq_longly=freq_longly,
                               diff=perf['seas_diffs'],
                               time_unit=freq_longly,
                               time=perf['time_features'])

        return expr_fmt
