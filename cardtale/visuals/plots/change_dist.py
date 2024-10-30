from typing import List

from cardtale.visuals.plot import Plot
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.base.violin_partial import PartialViolinPlot
from cardtale.visuals.base.density import PlotDensity
from cardtale.analytics.operations.tsa.distributions import KolmogorovSmirnov
from cardtale.cards.strings import gettext
from cardtale.core.utils.splits import DataSplit
from cardtale.visuals.config import PLOT_NAMES


class ChangeDistPlots(Plot):
    """
    Class for creating and analyzing change distribution plots.
    Using a partial violin plot and a density plot.

    Attributes:
        caption (str): Caption for the plot.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for change detection.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: List[str]):
        """
        Initializes the ChangeDistPlots class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for change detection.
            name (List[str]): Name(s) of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=True, name=name)

        self.caption = gettext('change_beforeafter_1st_caption')
        self.plot_name = PLOT_NAMES['change_dist']

        self.tests = tests

    def build(self, *args, **kwargs):
        """
        Creates the change distribution plot.
        """

        if self.show_me:
            cp, _ = self.tests.change.get_change_points()

            data_parts = DataSplit.change_partition(data=self.tsd.df,
                                                    cp_index=cp[0],
                                                    time_col=self.tsd.time_col,
                                                    target_col=self.tsd.target_col)

            parts_dist = PartialViolinPlot.partial_violin(data=data_parts,
                                                          x_axis_col='Part',
                                                          y_axis_col=self.tsd.target_col,
                                                          group_col=self.tsd.time_col)

            parts_dens = PlotDensity.by_pair(data_parts,
                                             x_axis_col=self.tsd.target_col,
                                             group_col='Part')

            self.plot = {'lhs': parts_dist, 'rhs': parts_dens}

    def analyse(self, *args, **kwargs):
        """
        Analyzes the change in distribution.

        The analysis includes checking for significant changes and identifying
        the best distributions before and after the change point.
        """

        cp, _ = self.tests.change.get_change_points()

        if len(cp) > 0:
            self.show_me = True

            s = self.tsd.get_target_series(df=self.tsd.df,
                                           time_col=self.tsd.time_col,
                                           target_col=self.tsd.target_col)

            change_in_dist = self.tests.change.change_significance(s)

            before, after = DataSplit.change_partition(s, cp[0], return_series=True)
            dist_bf, dist_af = KolmogorovSmirnov.best_dist_in_two_parts(before, after)

            if change_in_dist:
                chg_dist_analysis = gettext('change_beforeafter_1st_analysis_diff')
                self.analysis.append(chg_dist_analysis)

                if dist_bf == dist_af:
                    # if the dist are the same and None (no dist was found)
                    pass
                else:
                    # dists are diff
                    if dist_bf is None:
                        chg_best_dists = gettext('change_beforeafter_dists_p1none').format(dist_af)
                    elif dist_af is None:
                        chg_best_dists = gettext('change_beforeafter_dists_p2none').format(dist_bf)
                    else:
                        chg_best_dists = gettext('change_beforeafter_dists_p1p2').format(dist_bf, dist_af)

                    self.analysis.append(chg_best_dists)
            else:
                chg_dist_analysis = gettext('change_beforeafter_1st_analysis_nodiff')
                self.analysis.append(chg_dist_analysis)
