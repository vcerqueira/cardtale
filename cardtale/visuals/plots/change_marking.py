from typing import Optional

from cardtale.visuals.plot import Plot
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import gettext
from cardtale.visuals.config import PLOT_NAMES


class ChangesMarksPlot(Plot):
    """
    Class for creating and analyzing change marking plots.

    Attributes:
        caption (str): Caption for the plot.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for change detection.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: str):
        """
        Initializes the ChangesMarksPlot class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for change detection.
            name (str): Name of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.caption = gettext('change_line_plot_caption')
        self.plot_name = PLOT_NAMES['change_marking']

        self.tests = tests

    def build(self, *args, **kwargs):
        """
        Creates the change marking plot.
        """

        if self.show_me:
            _, cp_idx = self.tests.change.get_change_points()

            self.plot = \
                LinePlot.univariate_change(data=self.tsd.df,
                                           x_axis_col=self.tsd.time_col,
                                           y_axis_col=self.tsd.target_col,
                                           change_points=cp_idx)

    def analyse(self, *args, **kwargs):
        """
        Analyzes the change marking.

        The analysis includes identifying the number of change points and their characteristics.
        """

        cp, _ = self.tests.change.get_change_points()

        n_cp = len(cp)

        if n_cp < 1:
            self.show_me = False
            return

        self.show_me = True

        # assuming there's at least one change point
        plt_deq1 = self.deq_any_change_point()
        plt_deq2 = self.deq_change_point_effect()

        self.analysis = [plt_deq1, plt_deq2]
        self.analysis = [x for x in self.analysis if x is not None]

    def format_caption(self, plot_id: int):
        """
        Formats the caption with the respective number and method.

        Args:
            plot_id (int): Plot id.
        """

        self.img_data['caption'] = \
            self.img_data['caption'].format(plot_id, self.tests.change.method)

    def deq_any_change_point(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Are the any change points in the time series?

        Approach:
            - PELT testing
        """

        cp, _ = self.tests.change.get_change_points()

        n_cp = len(cp)

        if n_cp == 1:
            expr_fmt = gettext('change_line_1point')
        else:
            expr_fmt = gettext('change_line_npoints').format(n_cp)

        return expr_fmt

    def deq_change_point_effect(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): What is the effect of the change points?

        Approach:
            - PELT testing
        """

        cp, cp_idx = self.tests.change.get_change_points()

        n_cp = len(cp)

        cp_dir = 'an increasing' if self.tests.change.level_increased else 'a decreasing'
        cp_time = cp_idx[0].strftime(self.tsd.date_format)

        prefix = '' if n_cp == 1 else 'first '

        expr_fmt = gettext('change_line_analysis').format(prefix, cp_time, cp_dir)

        return expr_fmt
