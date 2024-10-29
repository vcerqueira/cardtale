import numpy as np
import pandas as pd

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import join_l, gettext
from cardtale.cards.parsers.trend import TrendTestsParser

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

    def build(self):
        """
        Creates the trend line plot.
        """

        df_ = self.tsd.df.copy()
        df_['Trend'] = self.tsd.stl_df['Trend']

        self.plot = LinePlot.univariate_w_support(data=df_,
                                                  x_axis_col=self.tsd.time_col,
                                                  y_axis_col_main='Trend',
                                                  y_axis_col_supp=self.tsd.target_col)

    def analyse(self):
        """
        Analyzes the trend line plot.

        The analysis includes summarizing the trend strength and correlation.
        """

        self.show_me, show_results = TrendTestsParser.show_trend_plots(self.tests.trend)

        if not self.show_me:
            return

        time_corr_avg = self.tests.trend.time_model.time_corr_avg
        corr_side = self.tests.trend.time_model.side

        trend, no_trend, level, no_level = self.tests.trend.results_in_list()

        dt = pd.Series(TREND_STRENGTH_INTERVAL) - np.abs(time_corr_avg)
        trend_label = dt[dt < 0].index[0]

        trend_analysis = gettext('trend_line_analysis1').format(join_l(trend))
        trend_analysis += gettext('trend_line_analysis2').format(trend_label, corr_side)
        self.analysis.append(trend_analysis)

        if len(no_trend) > 0:
            if len(no_trend) == 1:
                suffix = ''
            else:
                suffix = 's'

            no_trend_methods = gettext('trend_line_analysis3').format(suffix, join_l(no_trend))
            self.analysis.append(no_trend_methods)

        if len(level) > 0:
            lvl_anls = gettext('trend_line_analysis4').format(join_l(level))

            if len(no_level) > 0:
                lvl_anls += gettext('trend_line_analysis4ifany').format(join_l(no_level))
        else:
            lvl_anls = gettext('trend_line_analysis4none')

        self.analysis.append(lvl_anls)

        perf_t = TrendTestsParser.parse_t_performance(self.tests.trend)

        self.analysis.append(perf_t)
