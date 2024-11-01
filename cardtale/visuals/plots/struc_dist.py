from typing import List, Optional

import numpy as np

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.histogram import PlotHistogram
from cardtale.visuals.base.boxplot import Boxplot
from cardtale.visuals.base.violin_partial import PartialViolinPlot
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
        series_violinplot = PartialViolinPlot.univariate_flipped(data=self.tsd.df,
                                                              y_axis_col=self.tsd.target_col)

        self.plot = {'lhs': series_hist, 'rhs': series_violinplot}

    def analyse(self, *args, **kwargs):
        """
        Analyzes the time series distribution.

        The analysis includes checking for rejected distributions, outliers, skewness, and kurtosis.
        """

        plt_deq1 = self.deq_rejected_distr()
        plt_deq2 = self.deq_best_distr()
        plt_deq3 = self.deq_outliers()
        plt_deq4 = self.deq_skewness()
        plt_deq5 = self.deq_kurtosis()

        self.analysis = [
            plt_deq1,
            plt_deq2,
            plt_deq3,
            plt_deq4,
            plt_deq5,
        ]

        self.analysis = [x for x in self.analysis if x is not None]

    def deq_rejected_distr(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): What distributions do not fit the data?

        Approach:
            - Kolmorogov-Smirnov test
        """
        if len(self.tsd.summary.reject_dists) < 1:
            return None

        expr = gettext('series_dist_analysis1')

        expr_fmt = expr.format(join_l(self.tsd.summary.reject_dist_nms))

        return expr_fmt

    def deq_best_distr(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): What distribution best fits the data?

        Approach:
            - Kolmorogov-Smirnov test
        """
        n_rej_dists = self.tsd.summary.n_reject_dist_nms
        n_dists = len(n_rej_dists)

        # no distribution fits
        if n_dists == 0:
            expr_fmt = gettext('series_dist_analysis2_none')
            return expr_fmt
        else:
            best_dist = self.tsd.summary.n_reject_dist_nms[0]
            best_dist_pval = np.round(self.tsd.summary.n_reject_dists.iloc[0], 2)

        # only one distribution fits
        if n_dists == 1:
            expr = gettext('series_dist_analysis2_one')
            expr_fmt = expr.format(best_dist, best_dist_pval)
        else:
            # many distributions fit
            expr = gettext('series_dist_analysis2_many')
            other_dists = join_l(self.tsd.summary.n_reject_dist_nms[1:])

            expr_fmt = expr.format(best_dist, best_dist_pval, other_dists)

        return expr_fmt

    def deq_outliers(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Are there outliers in the time series?

        Approach:
            - Tukey's fences
        """

        # no outliers
        if self.tsd.summary.n_outliers < 1:
            return gettext('series_dist_analysis3fail')

        # all upper outliers
        if self.tsd.summary.perc_upp_outliers == 100:
            expr = gettext('series_dist_analysis3allupper')
            expr_fmt = expr.format(self.tsd.summary.n_outliers,
                                   self.tsd.summary.perc_outliers)
        else:
            expr = gettext('series_dist_analysis3')
            expr_fmt = expr.format(self.tsd.summary.n_outliers,
                                   self.tsd.summary.n_outliers_upper,
                                   self.tsd.summary.perc_upp_outliers,
                                   self.tsd.summary.perc_outliers)

        return expr_fmt

    def deq_kurtosis(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): How is the kurtosis of the time series?

        Approach:
            - Moments and KS test
        """

        krt = np.round(self.tsd.summary.stats['kurtosis'], 2)

        if not self.tsd.summary.reject_normal_kurtosis:
            expr = gettext('series_dist_analysis5_kurtosis_normal')
            expr_fmt = expr.format(krt)
        else:
            kurtosis_lab = 'light tailed' if krt < 0 else 'heavy tailed'

            expr = gettext('series_dist_analysis5_kurtosis_notnormal')
            expr_fmt = expr.format(krt, kurtosis_lab)

        return expr_fmt

    def deq_skewness(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): How is the skewness of the time series?

        Approach:
            - Moments and KS test
        """

        skwn = np.round(self.tsd.summary.stats['skew'], 2)

        if not self.tsd.summary.reject_normal_skewness:
            side = 'left' if self.tsd.summary.stats['skew'] < 0 else 'right'

            expr = gettext('series_dist_analysis4_skew_symmetric')
            expr_fmt = expr.format(skwn, side)
        else:
            if self.tsd.summary.stats['skew'] < 0:
                expr = gettext('series_dist_analysis4_skew_asymmetric')
                expr_fmt = expr.format(skwn, 'left', 'right')
            else:
                expr = gettext('series_dist_analysis4_skew_asymmetric')
                expr_fmt = expr.format(skwn, 'right', 'left')

        return expr_fmt
