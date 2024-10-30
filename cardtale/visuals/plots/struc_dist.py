from typing import List

import numpy as np

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.histogram import PlotHistogram
from cardtale.visuals.base.boxplot import Boxplot
from cardtale.core.data import TimeSeriesData
from cardtale.visuals.config import PLOT_NAMES
from cardtale.cards.strings import join_l, gettext


class SeriesDistPlots(Plot):
    """
    Class for creating and analyzing time series distribution plots.

    Attributes:
        caption (str): Caption for the plot.
        show_me (bool): Flag indicating if the plot should be shown.
        plot_name (str): Name of the plot.
    """

    def __init__(self, tsd: TimeSeriesData, name: List[str]):
        """
        Initializes the SeriesDistPlots class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            name (List[str]): Name(s) of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=True, name=name)

        self.caption = gettext('series_dist_caption')
        self.show_me = True
        self.plot_name = PLOT_NAMES['struc_dist']

    def build(self, *args, **kwargs):
        """
        Creates the time series distribution plots.
        """

        # Time series distribution w/ histogram
        series_hist = PlotHistogram.univariate(data=self.tsd.df,
                                               x_axis_col=self.tsd.target_col,
                                               n_bins=15)

        # Time series distribution w/ boxplot
        series_boxplot = Boxplot.univariate_flipped(data=self.tsd.df,
                                                    y_axis_col=self.tsd.target_col)

        self.plot = {'lhs': series_hist, 'rhs': series_boxplot}

    def analyse(self, *args, **kwargs):
        """
        Analyzes the time series distribution.

        The analysis includes checking for rejected distributions, outliers, skewness, and kurtosis.
        """

        if len(self.tsd.summary.reject_dists) > 0:
            dist_anl_1 = gettext('series_dist_analysis1').format(join_l(self.tsd.summary.reject_dist_nms))
            self.analysis.append(dist_anl_1)

        n_rej_dists = self.tsd.summary.n_reject_dist_nms
        if len(n_rej_dists) == 0:
            dist_anl_2 = gettext('series_dist_analysis2_none')
        elif len(n_rej_dists) == 1:
            dist_anl_2 = gettext('series_dist_analysis2_one')
            dist_anl_2 = dist_anl_2.format(self.tsd.summary.n_reject_dist_nms[0],
                                           np.round(self.tsd.summary.n_reject_dists[0], 2))
        else:
            dist_anl_2 = gettext('series_dist_analysis2_many')
            dist_anl_2 = dist_anl_2.format(self.tsd.summary.n_reject_dist_nms[0],
                                           np.round(self.tsd.summary.n_reject_dists.iloc[0], 2),
                                           join_l(self.tsd.summary.n_reject_dist_nms[1:]))

        self.analysis.append(dist_anl_2)

        if self.tsd.summary.n_outliers > 0:
            if self.tsd.summary.perc_upp_outliers == 100:
                bp_outlier_analysis = \
                    gettext('series_dist_analysis3allupper').format(self.tsd.summary.n_outliers,
                                                                    self.tsd.summary.perc_outliers)
            else:
                bp_outlier_analysis = \
                    gettext('series_dist_analysis3').format(self.tsd.summary.n_outliers,
                                                            self.tsd.summary.n_outliers_upper,
                                                            self.tsd.summary.perc_upp_outliers,
                                                            self.tsd.summary.perc_outliers)
        else:
            bp_outlier_analysis = gettext('series_dist_analysis3fail')

        self.analysis.append(bp_outlier_analysis)

        if not self.tsd.summary.reject_normal_skewness:
            if self.tsd.summary.stats['skew'] < 0:
                side = 'left'
            else:
                side = 'right'
            skewness_analysis = gettext('series_dist_analysis4_skew_symmetric'). \
                format(np.round(self.tsd.summary.stats['skew'], 2), side)
        else:
            if self.tsd.summary.stats['skew'] < 0:
                skewness_analysis = gettext('series_dist_analysis4_skew_asymmetric'). \
                    format(np.round(self.tsd.summary.stats['skew'], 2), 'left', 'right')
            else:
                skewness_analysis = gettext('series_dist_analysis4_skew_asymmetric'). \
                    format(np.round(self.tsd.summary.stats['skew'], 2), 'right', 'left')

        if not self.tsd.summary.reject_normal_kurtosis:
            kurtosis_analysis = gettext('series_dist_analysis5_kurtosis_normal'). \
                format(np.round(self.tsd.summary.stats['kurtosis'], 2))
        else:
            if self.tsd.summary.stats['kurtosis'] < 0:
                kurtosis_lab = 'light tailed'
            else:
                kurtosis_lab = 'heavy tailed'

            kurtosis_analysis = gettext('series_dist_analysis5_kurtosis_notnormal'). \
                format(np.round(self.tsd.summary.stats['kurtosis'], 2), kurtosis_lab)

        self.analysis.append(kurtosis_analysis)
        self.analysis.append(skewness_analysis)
