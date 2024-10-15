from typing import List

import numpy as np

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.histogram import PlotHistogram
from cardtale.visuals.base.boxplot import Boxplot

from cardtale.data.uvts import UVTimeSeries
from cardtale.visuals.config import SERIES, PLOT_NAMES
from cardtale.cards.strings import join_l, gettext


class SeriesDistPlots(Plot):

    def __init__(self, name: List[str], data: UVTimeSeries):
        super().__init__(data=data, multi_plot=True, name=name)

        self.caption = gettext('series_dist_caption')
        self.show_me = True

        self.plot_name = PLOT_NAMES['struc_dist']

    def build(self):
        # Time series distribution w/ histogram
        series_hist = PlotHistogram.univariate(data=self.data.df,
                                               x_axis_col=SERIES,
                                               n_bins=15)

        # Time series distribution w/ boxplot
        series_boxplot = Boxplot.univariate_flipped(data=self.data.df,
                                                    y_axis_col=SERIES)

        self.plot = {'lhs': series_hist, 'rhs': series_boxplot}

    def analyse(self):

        if len(self.data.summary.reject_dists) > 0:
            dist_anl_1 = gettext('series_dist_analysis1').format(join_l(self.data.summary.reject_dist_nms))
            self.analysis.append(dist_anl_1)

        n_rej_dists = self.data.summary.n_reject_dist_nms
        if len(n_rej_dists) == 0:
            dist_anl_2 = gettext('series_dist_analysis2_none')
        elif len(n_rej_dists) == 1:
            dist_anl_2 = gettext('series_dist_analysis2_one')
            dist_anl_2 = dist_anl_2.format(self.data.summary.n_reject_dist_nms[0],
                                           np.round(self.data.summary.n_reject_dists[0], 2))
        else:
            dist_anl_2 = gettext('series_dist_analysis2_many')
            dist_anl_2 = dist_anl_2.format(self.data.summary.n_reject_dist_nms[0],
                                           np.round(self.data.summary.n_reject_dists[0], 2),
                                           join_l(self.data.summary.n_reject_dist_nms[1:]))

        self.analysis.append(dist_anl_2)

        if self.data.summary.n_outliers > 0:
            if self.data.summary.perc_upp_outliers == 100:
                bp_outlier_analysis = \
                    gettext('series_dist_analysis3allupper').format(self.data.summary.n_outliers,
                                                                    self.data.summary.perc_outliers)
            else:
                bp_outlier_analysis = \
                    gettext('series_dist_analysis3').format(self.data.summary.n_outliers,
                                                            self.data.summary.n_outliers_upper,
                                                            self.data.summary.perc_upp_outliers,
                                                            self.data.summary.perc_outliers)


        else:
            bp_outlier_analysis = gettext('series_dist_analysis3fail')

        self.analysis.append(bp_outlier_analysis)

        if not self.data.summary.reject_normal_skewness:
            if self.data.summary.stats['skew'] < 0:
                side = 'left'
            else:
                side = 'right'
            skewness_analysis = gettext('series_dist_analysis4_skew_symmetric'). \
                format(np.round(self.data.summary.stats['skew'], 2), side)
        else:
            if self.data.summary.stats['skew'] < 0:
                skewness_analysis = gettext('series_dist_analysis4_skew_asymmetric'). \
                    format(np.round(self.data.summary.stats['skew'], 2), 'left', 'right')
            else:
                skewness_analysis = gettext('series_dist_analysis4_skew_asymmetric'). \
                    format(np.round(self.data.summary.stats['skew'], 2), 'right', 'left')

        if not self.data.summary.reject_normal_kurtosis:
            kurtosis_analysis = gettext('series_dist_analysis5_kurtosis_normal'). \
                format(np.round(self.data.summary.stats['kurtosis'], 2))
        else:
            if self.data.summary.stats['kurtosis'] < 0:
                kurtosis_lab = 'light tailed'
            else:
                kurtosis_lab = 'heavy tailed'

            kurtosis_analysis = gettext('series_dist_analysis5_kurtosis_notnormal'). \
                format(np.round(self.data.summary.stats['kurtosis'], 2), kurtosis_lab)

        self.analysis.append(kurtosis_analysis)
        self.analysis.append(skewness_analysis)
