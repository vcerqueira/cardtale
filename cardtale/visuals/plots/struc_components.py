from typing import Optional

from cardtale.core.data import TimeSeriesData
from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import gettext, join_l
from cardtale.analytics.testing.base import TestingComponents

from cardtale.core.config.analysis import DECOMPOSITION_METHOD
from cardtale.visuals.config import PLOT_NAMES


class SeriesComponentsPlot(Plot):
    """
    Class for creating and analyzing time series components plots.

    Attributes:
        caption (str): Caption for the plot.
        show_me (bool): Flag indicating if the plot should be shown.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for seasonality and trend analysis.
    """

    HEIGHT = 5.25

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: str):
        """
        Initializes the SeriesComponentsPlot class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for seasonality and trend analysis.
            name (str): Name of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.caption = gettext('series_components_caption')
        self.show_me = True
        self.plot_name = PLOT_NAMES['struc_components']

        self.tests = tests

    def build(self, *args, **kwargs):
        """
        Creates the components plot.
        """

        self.plot = LinePlot.multivariate_grid(data=self.tsd.stl_df,
                                               x_axis_col=self.tsd.time_col,
                                               category_list=['Trend', 'Seasonal', 'Residuals'],
                                               scales='free')

    def analyse(self, *args, **kwargs):
        """
        Analyzes the components plot.

        The analysis includes identifying significant trends and seasonal patterns.
        """

        plt_deq1 = self.deq_trend_component()
        plt_deq2 = self.deq_seasonal_component()
        plt_deq3 = self.deq_residuals_component()

        self.analysis = [plt_deq1, plt_deq2, plt_deq3]

        self.analysis = [x for x in self.analysis if x is not None]

    def format_caption(self, plot_id: int):
        """
        Formats the caption with the respective number and method.

        Args:
            plot_id (int): Plot id.
        """

        self.img_data['caption'] = self.img_data['caption'].format(plot_id, DECOMPOSITION_METHOD)

    def deq_trend_component(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Is there a strong trend component in the time series?

        todo measure trend strength

        Approach:
            - Decomposition analysis
        """

        trend, no_trend, _, _ = self.tests.trend.results_in_list()

        if len(no_trend) == 0:
            expr = gettext('series_components_analysis_trend_all1')
            expr_fmt = expr.format(join_l(trend))
        elif len(trend) == 0:
            expr = gettext('series_components_analysis_trend_all0')
            expr_fmt = expr.format(join_l(no_trend))
        else:
            expr = gettext('series_components_analysis_trend_mix')
            expr_fmt = expr.format(join_l(trend), join_l(no_trend))

        return expr_fmt

    def deq_seasonal_component(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Is there a strong seasonal component in the time series?

        todo measure seasonal strength, at various levels

        Approach:
            - Decomposition analysis
        """

        seas_t = self.tests.seasonality.seas_tests_on_main

        if all(seas_t > 0):
            expr = gettext('series_components_analysis_seas_all1')
            expr_fmt = expr.format(join_l(seas_t.index))
        elif all(seas_t < 1):
            expr = gettext('series_components_analysis_seas_all0')
            expr_fmt = expr.format(join_l(seas_t.index))
        else:
            expr = gettext('series_components_analysis_seas_mix')
            expr_fmt = expr.format(join_l(seas_t[seas_t > 0].index),
                                   join_l(seas_t[seas_t < 1].index))

        return expr_fmt

    def deq_residuals_component(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): What is the structure of the residuals based on an STL decomposition?

        Approach:
            - Decomposition analysis
        """

        expr_fmt = 'ANALYSE RESIDUALS'

        return expr_fmt
