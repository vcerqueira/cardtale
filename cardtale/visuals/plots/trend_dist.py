from typing import List

import numpy as np

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.histogram import PlotHistogram
from cardtale.visuals.base.scatterplot import Scatterplot

from cardtale.cards.strings import join_l, gettext
from cardtale.analytics.tsa.tde import TimeDelayEmbedding
from cardtale.analytics.testing.components.trend import TrendShowTests

from cardtale.data.uvts import UVTimeSeries
from cardtale.visuals.config import SERIES, PLOT_NAMES


class TrendDistPlots(Plot):

    def __init__(self, name: List[str], data: UVTimeSeries):
        super().__init__(data=data, multi_plot=True, name=name)

        self.caption = gettext('trend_lagplot_dhist_caption')

        self.plot_name = PLOT_NAMES['trend_dist']

    def build(self):
        """

        """
        series_df = TimeDelayEmbedding.ts_as_supervised(self.data.series, horizon=0, n_lags=2)

        trend_lagplot = Scatterplot.lagplot(data=series_df,
                                            x_axis_col='t-1',
                                            y_axis_col='t',
                                            add_perfect_abline=True,
                                            x_lab='Series at time t',
                                            y_lab='Series at time t+1')

        diff_df = self.data.series.pct_change()[1:].reset_index()

        trend_dhist = PlotHistogram.univariate(data=diff_df,
                                               x_axis_col=SERIES,
                                               n_bins=15,
                                               x_lab='% Change',
                                               y_lab='Count')

        self.plot = {'lhs': trend_dhist, 'rhs': trend_lagplot}

    def analyse(self):
        tests = self.data.tests.trend

        self.show_me, show_results = TrendShowTests.show_distribution_plot(tests)

        if not self.show_me:
            return

        diff_stats = self.data.diff_summary

        if len(diff_stats.reject_dists) > 0:
            format_txt_d1 = f'{join_l(diff_stats.reject_dist_nms)}.'
            analysis_dist1 = gettext('trend_diff_dist_analysis1').format(format_txt_d1)

            self.analysis.append(analysis_dist1)

        if len(diff_stats.n_reject_dist_nms) > 0:
            analysis_dist2 = gettext('trend_diff_dist_analysis2')
            analysis_dist2 = \
                analysis_dist2.format(diff_stats.n_reject_dist_nms[0],
                                      np.round(diff_stats.n_reject_dists[0], 2),
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

        self.analysis.append(tests.parse_differencing_performance())
