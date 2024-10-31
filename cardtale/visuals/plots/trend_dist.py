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

        mlf = MLForecast(models=[], freq=self.tsd.dt.freq, lags=[1])

        lagged_df = mlf.preprocess(df=self.tsd.df)
        lagged_df = lagged_df[[self.tsd.target_col, 'lag1']]
        lagged_df.columns = ['t', 't-1']

        trend_lagplot = Scatterplot.lagplot(data=lagged_df,
                                            x_axis_col='t-1',
                                            y_axis_col='t',
                                            add_perfect_abline=True,
                                            x_lab=f'{self.tsd.target_col} at time t',
                                            y_lab=f'{self.tsd.target_col} at time t+1')

        diff_df = s.pct_change()[1:].reset_index()

        trend_dhist = PlotHistogram.univariate(data=diff_df,
                                               x_axis_col=self.tsd.target_col,
                                               n_bins=15,
                                               x_lab='% Change',
                                               y_lab='Count')

        self.plot = {'lhs': trend_dhist, 'rhs': trend_lagplot}

    def analyse(self, *args, **kwargs):
        """
        Analyzes the trend distribution plots.

        The analysis includes checking for rejected distributions, outliers, skewness, and kurtosis.
        """

        self.show_me, _ = TrendTestsParser.show_trend_plots(self.tests.trend)

        if not self.show_me:
            return

        plt_deq1 = self.deq_diff_reject_distr()
        plt_deq2 = self.deq_diff_best_distr()
        plt_deq3 = self.deq_diff_skewness()
        plt_deq4 = self.deq_diff_kurtosis()
        plt_deq5 = self.deq_accuracy_differencing()

        self.analysis = [plt_deq1, plt_deq2, plt_deq3, plt_deq4, plt_deq5]
        self.analysis = [x for x in self.analysis if x is not None]

    def deq_diff_reject_distr(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): What distributions do not fit the differenced time series?

        Approach:
            - Differencing + KS test
        """

        diff_stats = self.tsd.diff_summary

        if len(diff_stats.reject_dists) > 0:
            expr = gettext('trend_diff_dist_analysis1')
            expr_fmt = expr.format(join_l(diff_stats.reject_dist_nms))
        else:
            expr_fmt = None

        return expr_fmt

    def deq_diff_best_distr(self) -> Optional[str]:
        """
        DEQ: What distribution best fits the differenced time series?

        Approach:
            - Differencing + KS test
        """

        diff_stats = self.tsd.diff_summary

        if len(diff_stats.n_reject_dist_nms) > 0:
            expr = gettext('trend_diff_dist_analysis2')

            best_distr = diff_stats.n_reject_dist_nms[0]
            best_distr_pv = np.round(diff_stats.n_reject_dists.iloc[0], 2)

            expr_fmt = expr.format(best_distr, best_distr_pv, join_l(diff_stats.n_reject_dist_nms[1:]))
        else:
            expr_fmt = gettext('trend_diff_dist_analysis2none')

        return expr_fmt

    def deq_diff_skewness(self) -> Optional[str]:
        """
        DEQ: What's the skewness of the differenced time series like?

        Approach:
            - Differencing + stats
        """

        diff_stats = self.tsd.diff_summary
        skwn = np.round(diff_stats.stats['skew'], 2)

        if not diff_stats.reject_normal_skewness:
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

    def deq_diff_kurtosis(self) -> Optional[str]:
        """
        DEQ: What's the skewness of the differenced time series like?

        Approach:
            - Differencing + stats
        """

        diff_stats = self.tsd.diff_summary
        krt = np.round(diff_stats.stats['kurtosis'], 2)

        if not diff_stats.reject_normal_kurtosis:
            expr = gettext('trend_diff_dist_analysis5_kurtosis_normal')
            expr_fmt = expr.format(krt)

        else:
            krt_lab = 'light tailed' if krt < 0 else 'heavy tailed'

            expr = gettext('trend_diff_dist_analysis5_kurtosis_notnormal')
            expr_fmt = expr.format(krt, krt_lab)

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
