from typing import Optional

import numpy as np
import pandas as pd

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import join_l, gettext
from cardtale.analytics.testing.card.trend import TrendTestsParser
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import PLOT_NAMES
from cardtale.core.config.analysis import TREND_STRENGTH_INTERVAL


class TrendLinePlot(Plot):
    """
    Class for creating and analyzing trend line plots.

    Attributes:
        caption (str): Caption for the plot.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for trend analysis.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: str):
        """
        Initializes the TrendLinePlot class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for trend analysis.
            name (str): Name of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.caption = gettext('trend_line_plot_caption')
        self.plot_name = PLOT_NAMES['trend_line']
        self.tests = tests

    def build(self, *args, **kwargs):
        """
        Creates the trend line plot.
        """

        df_ = self.tsd.df.copy()
        df_['Trend'] = self.tsd.stl_df['Trend']

        self.plot = LinePlot.univariate_w_support(data=df_,
                                                  x_axis_col=self.tsd.time_col,
                                                  y_axis_col_main='Trend',
                                                  y_axis_col_supp=self.tsd.target_col)

    def analyse(self, *args, **kwargs):
        """
        Analyzes the trend line plot.

        The analysis includes summarizing the trend strength and correlation.
        """

        self.show_me, _ = TrendTestsParser.show_trend_plots(self.tests.trend)

        if not self.show_me:
            return

        plt_deq1 = self.deq_trend_stationarity()
        plt_deq2 = self.deq_level_stationarity()
        plt_deq3 = self.deq_accuracy_rowid_feature()

        self.analysis = [plt_deq1, plt_deq2, plt_deq3]
        self.analysis = [x for x in self.analysis if x is not None]

    def deq_trend_stationarity(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): What's the trend like?

        Approach:
            - Unit root tests
        """

        time_corr_avg = self.tests.trend.time_model.time_corr_avg
        corr_side = self.tests.trend.time_model.side

        trend, no_trend, *_ = self.tests.trend.results_in_list()

        dt = pd.Series(TREND_STRENGTH_INTERVAL) - np.abs(time_corr_avg)
        trend_label = dt[dt < 0].index[0]

        expr_fmt = gettext('trend_line_analysis2').format(trend_label, corr_side)
        if len(trend) > 0:
            plural_str_t = 's' if len(trend) > 1 else ''
            expr_fmt += gettext('trend_line_analysis1').format(plural_str=plural_str_t,
                                                               tests=join_l(trend))
            lead_expr = 'But, the'
        else:
            lead_expr = 'The'

        if len(no_trend) > 0:
            plural_str_nt = 's' if len(no_trend) > 1 else ''
            expr_fmt += gettext('trend_line_analysis3').format(lead_expr=lead_expr,
                                                               plural_str=plural_str_nt,
                                                               tests=join_l(no_trend))

        return expr_fmt

    def deq_level_stationarity(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): What's the long-term level like?

        Approach:
            - Unit root tests
        """

        _, _, level, no_level = self.tests.trend.results_in_list()

        expr_lead = gettext('trend_line_level_lead')
        # all 0, len(no_level)=3, len(level)=0
        if len(level) < 1:
            expr_fmt = expr_lead + gettext('trend_line_level_all_0')
            return expr_fmt

        # len(no_level)=0, len(level)=3
        if len(no_level) < 1:
            expr_fmt = expr_lead + gettext('trend_line_level_all_1')
            return expr_fmt

        expr = gettext('trend_line_level_mix')
        # at least one in each

        plural_str1 = 's' if len(level) > 1 else ''
        plural_str0 = 's' if len(no_level) > 1 else ''

        expr_fmt = expr_lead + expr.format(plural_str1=plural_str1,
                                           tests1=join_l(level),
                                           plural_str0=plural_str0,
                                           tests0=join_l(no_level))

        return expr_fmt

    def deq_accuracy_rowid_feature(self) -> Optional[str]:
        """
        DEQ: Does a rowid feature improve forecasting accuracy?

        Approach:
            - Row id feature extraction + CV with landmark
        """

        perf = self.tests.trend.performance

        base = np.round(perf['base'], 2)
        t_feat = np.round(perf['trend_feature'], 2)

        t_improves = perf['base'] > perf['trend_feature']

        if t_improves:
            expr = gettext('trend_line_analysis_t_good')
        else:
            expr = gettext('trend_line_analysis_t_bad')

        expr_fmt = expr.format(base, t_feat)

        return expr_fmt
