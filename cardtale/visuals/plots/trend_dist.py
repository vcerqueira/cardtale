from typing import List, Optional

import numpy as np
from mlforecast import MLForecast

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.histogram import PlotHistogram
from cardtale.visuals.base.scatterplot import Scatterplot

from cardtale.cards.strings import join_l, gettext
from cardtale.analytics.testing.card.trend import TrendTestsParser

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.analytics.operations.tsa.log import LogTransformation
from cardtale.visuals.config import PLOT_NAMES


class TrendDistPlots(Plot):
    """
    Class for creating and analyzing trend distribution plots.

    Attributes:
        caption (str): Caption for the plot.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for trend analysis.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: List[str]):
        """
        Initializes the TrendDistPlots class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for trend analysis.
            name (List[str]): Name(s) of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=True, name=name)

        self.caption = gettext('trend_lagplot_dhist_caption')

        self.plot_name = PLOT_NAMES['trend_dist']
        self.tests = tests

    def build(self, *args, **kwargs):
        """
        Creates the trend distribution plots.
        """

        s = self.tsd.get_target_series(df=self.tsd.df,
                                       time_col=self.tsd.time_col,
                                       target_col=self.tsd.target_col)

        mlf = MLForecast(models=[], freq=self.tsd.dt.freq_short, lags=[1])

        lagged_df = mlf.preprocess(df=self.tsd.df)
        lagged_df = lagged_df[[self.tsd.target_col, 'lag1']]
        lagged_df.columns = ['t', 't-1']

        trend_lagplot = Scatterplot.lagplot(data=lagged_df,
                                            x_axis_col='t-1',
                                            y_axis_col='t',
                                            add_perfect_abline=True,
                                            x_lab=f'{self.tsd.target_col} at time t',
                                            y_lab=f'{self.tsd.target_col} at time t+1')

        # diff_df = s.pct_change()[1:].reset_index()
        rets_df = LogTransformation.returns(s)[1:].reset_index()

        trend_dhist = PlotHistogram.univariate(data=rets_df,
                                               x_axis_col=self.tsd.target_col,
                                               n_bins=15,
                                               x_lab='Log returns',
                                               y_lab='Count')

        self.plot = {'lhs': trend_dhist, 'rhs': trend_lagplot}

    def analyse(self, *args, **kwargs):
        """
        Analyzes the trend distribution plots.

        # todo lagplot (check nist) analysis
        ## .. maybe not...already done on ACF??

        The analysis includes checking for rejected distributions, outliers, skewness, and kurtosis.
        """

        self.show_me, _ = TrendTestsParser.show_trend_plots(self.tests.trend)

        if not self.show_me:
            return

        plt_deq1 = self.deq_dist_log_returns()
        plt_deq2 = self.deq_logdiff_skewness()
        plt_deq3 = self.deq_logdiff_kurtosis()
        plt_deq4 = self.deq_log_returns_magnitudes()
        plt_deq5 = self.deq_log_returns_extrema()
        plt_deq6 = self.deq_accuracy_differencing()

        plt_deq1_2_3 = plt_deq1 + ' ' + plt_deq2 + ' ' + plt_deq3

        self.analysis = [plt_deq1_2_3, plt_deq4, plt_deq5, plt_deq6]
        self.analysis = [x for x in self.analysis if x is not None]

    def deq_dist_log_returns(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): How is the distribution of the log returns?

        Approach:
            - Log Differencing + stats
        """

        expr = gettext('trend_logdiff_dist')
        expr_fmt = expr.format(self.tsd.summary.growth['average_ret'],
                               self.tsd.summary.growth['median_ret'],
                               self.tsd.summary.growth['growth_vol'])

        return expr_fmt

    def deq_logdiff_skewness(self) -> Optional[str]:
        """
        DEQ: What's the skewness of the log differenced time series like?

        Approach:
            - Differencing + stats
        """

        skwn = np.round(self.tsd.summary.growth['skewness'], 2)
        skewness_like_normal = self.tsd.summary.growth['skewness_like_normal']

        if skewness_like_normal:
            side = 'left' if skwn < 0 else 'right'

            expr = gettext('trend_diff_dist_analysis4_skew_symmetric')
            expr_fmt = expr.format(skwn, side)
        else:
            if skwn < 0:
                expr = gettext('series_dist_analysis4_skew_asymmetric')
                expr_fmt = expr.format(skwn, 'left', 'right')
            else:
                expr = gettext('trend_diff_dist_analysis4_skew_asymmetric')
                expr_fmt = expr.format(skwn, 'right', 'left')

        return expr_fmt

    def deq_logdiff_kurtosis(self) -> Optional[str]:
        """
        DEQ: What's the skewness of the differenced time series like?

        Approach:
            - Differencing + stats
        """

        krt = np.round(self.tsd.summary.growth['kurtosis'], 2)

        if self.tsd.summary.growth['kurtosis_like_normal']:
            expr = gettext('trend_diff_dist_analysis5_kurtosis_normal')
            expr_fmt = expr.format(krt)
        else:
            krt_lab = 'light tailed' if krt < 0 else 'heavy tailed'

            expr = gettext('trend_diff_dist_analysis5_kurtosis_notnormal')
            expr_fmt = expr.format(krt, krt_lab)

        return expr_fmt

    def deq_log_returns_magnitudes(self) -> Optional[str]:
        """

        DEQ (Data Exploratory Question): What is the magnitude and direction of the log returns?

        Approach:
            - Log Differencing + stats
        """

        expr = gettext('trend_logdiff_magnitudes')
        expr_fmt = expr.format(self.tsd.summary.growth['upward_moves_prob'],
                               self.tsd.summary.growth['upward_moves_mag'],
                               self.tsd.summary.growth['downward_moves_prob'],
                               self.tsd.summary.growth['downward_moves_mag'],
                               self.tsd.summary.growth['direction_changes'],
                               self.tsd.summary.growth['direction_changes_perc'])

        return expr_fmt

    def deq_log_returns_extrema(self) -> Optional[str]:
        """

        DEQ (Data Exploratory Question): What is the behaviors of the log returns in the tails?

        Approach:
            - Log Differencing + stats
        """

        expr = gettext('trend_logdiff_extrema')
        expr_fmt = expr.format(self.tsd.summary.growth['extreme_pct'],
                               self.tsd.summary.growth['largest_increase'],
                               self.tsd.summary.growth['largest_increase_loc'],
                               self.tsd.summary.growth['largest_decrease'],
                               self.tsd.summary.growth['largest_decrease_loc'])

        return expr_fmt

    def deq_accuracy_differencing(self) -> Optional[str]:
        """
        DEQ: Does differencing improve forecasting accuracy?

        Approach:
            - Differencing + CV with landmark
        """

        perf = self.tests.trend.performance

        diff_improves = perf['base'] > perf['first_differences']

        if diff_improves:
            expr_fmt = gettext('trend_line_analysis_diff_good')
        else:
            expr_fmt = gettext('trend_line_analysis_diff_bad')

        return expr_fmt
