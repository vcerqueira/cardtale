from typing import List

import numpy as np
from mlforecast import MLForecast

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.histogram import PlotHistogram
from cardtale.visuals.base.scatterplot import Scatterplot

from cardtale.cards.strings import join_l, gettext
from cardtale.cards.parsers.trend import TrendTestsParser

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

        diff_stats = self.tsd.diff_summary

        if len(diff_stats.reject_dists) > 0:
            format_txt_d1 = f'{join_l(diff_stats.reject_dist_nms)}.'
            analysis_dist1 = gettext('trend_diff_dist_analysis1').format(format_txt_d1)

            self.analysis.append(analysis_dist1)

        if len(diff_stats.n_reject_dist_nms) > 0:
            analysis_dist2 = gettext('trend_diff_dist_analysis2')
            analysis_dist2 = \
                analysis_dist2.format(diff_stats.n_reject_dist_nms[0],
                                      np.round(diff_stats.n_reject_dists.iloc[0], 2),
                                      f'{join_l(diff_stats.n_reject_dist_nms[1:])}.')
        else:
            analysis_dist2 = gettext('trend_diff_dist_analysis2none')

        self.analysis.append(analysis_dist2)

        if not diff_stats.reject_normal_skewness:
            if diff_stats.stats['skew'] < 0:
                side = 'left'
            else:
                side = 'right'
            skewness_analysis = gettext('trend_diff_dist_analysis4_skew_symmetric'). \
                format(np.round(diff_stats.stats['skew'], 2), side)
        else:
            if diff_stats.stats['skew'] < 0:
                skewness_analysis = gettext('series_dist_analysis4_skew_asymmetric'). \
                    format(np.round(diff_stats.stats['skew'], 2), 'left', 'right')
            else:
                skewness_analysis = gettext('trend_diff_dist_analysis4_skew_asymmetric'). \
                    format(np.round(diff_stats.stats['skew'], 2), 'right', 'left')

        if not diff_stats.reject_normal_kurtosis:
            kurtosis_analysis = gettext('trend_diff_dist_analysis5_kurtosis_normal'). \
                format(np.round(diff_stats.stats['kurtosis'], 2))
        else:
            if diff_stats.stats['kurtosis'] < 0:
                kurtosis_lab = 'light tailed'
            else:
                kurtosis_lab = 'heavy tailed'

            kurtosis_analysis = gettext('trend_diff_dist_analysis5_kurtosis_notnormal'). \
                format(np.round(diff_stats.stats['kurtosis'], 2), kurtosis_lab)

        self.analysis.append(kurtosis_analysis)
        self.analysis.append(skewness_analysis)

        perf_diff = TrendTestsParser.parse_differencing_performance(self.tests.trend)

        self.analysis.append(perf_diff)
