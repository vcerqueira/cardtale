from typing import List, Optional

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.summary import SummaryStatPlot

from cardtale.cards.strings import gettext
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import PLOT_NAMES

MEAN_AND_STD = 'mean and standard deviation'
MEAN_ONLY = 'mean'
STD_ONLY = 'standard deviation'


class SeasonalSummaryPlots(Plot):
    """
    Class for creating and analyzing seasonal summary plots.

    Attributes:
        plot_id (str): Identifier for the plot.
        named_seasonality (str): Named seasonality for the plot.
        caption (str): Caption for the plot.
        x_axis_col (str): Column name for the x-axis.
        caption_expr (str): Expression for the caption.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for seasonality.
    """

    def __init__(self,
                 tsd: TimeSeriesData,
                 tests: TestingComponents,
                 name: List[str],
                 named_seasonality: str,
                 x_axis_col: str):
        """
        Initializes the SeasonalSummaryPlots class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for seasonality.
            name (List[str]): Name(s) of the plot.
            named_seasonality (str): Named seasonality for the plot.
            x_axis_col (str): Column name for the x-axis.
        """

        super().__init__(tsd=tsd, multi_plot=True, name=name)

        self.plot_id = 'seas_summary'

        self.named_seasonality = named_seasonality
        self.caption = gettext('seasonality_summary_plot_caption')

        self.x_axis_col = x_axis_col

        self.caption_expr = f'{self.x_axis_col}ly'

        self.plot_name = PLOT_NAMES[self.plot_id]
        self.plot_name += f' ({self.x_axis_col}ly)'

        self.tests = tests

    def build(self, *args, **kwargs):
        """
        Creates the seasonal summary plot.
        """

        mean_plot = SummaryStatPlot.summary_plot(data=self.tsd.seas_df,
                                                 group_col=self.x_axis_col,
                                                 y_col=self.tsd.target_col,
                                                 func='mean',
                                                 y_lab='Mean')

        std_plot = SummaryStatPlot.summary_plot(data=self.tsd.seas_df,
                                                group_col=self.x_axis_col,
                                                y_col=self.tsd.target_col,
                                                func='std',
                                                y_lab='Standard Deviation')

        self.plot = {'lhs': mean_plot, 'rhs': std_plot}

    def analyse(self, *args, **kwargs):
        """
        Analyzes the seasonal summary plot.

        The analysis includes checking for significant differences in means and standard deviations.
        """

        if self.tests.seasonality.tests[self.named_seasonality].metadata['show_summary_plot']:
            self.show_me = True
        else:
            return

        plt_deq1 = self.deq_group_differences()

        self.analysis = [plt_deq1]
        self.analysis = [x for x in self.analysis if x is not None]

    def format_caption(self, plot_id: int):
        """
        Formats the caption with the respective number and method.

        Args:
            plot_id (int): Plot id.
        """

        self.img_data['caption'] = \
            self.img_data['caption'].format(plot_id, self.caption_expr.lower())

    def deq_group_differences(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Are there statistical differences in the time series groups?

        Approach:
            - anova_test
            - kruskal_test
            - levene_test
            - bartlett_test
        """

        tests = self.tests.seasonality.get_tests_by_named_seasonality(self.named_seasonality)

        rej_mean, rej_std = tests.group_tests_b['eq_means'], tests.group_tests_b['eq_std']

        if rej_mean and rej_std:
            expr = gettext('seasonality_summary_plot_analysis')
            expr_fmt = expr.format(MEAN_AND_STD, self.x_axis_col.lower())
        elif rej_mean and not rej_std:
            expr = gettext('seasonality_summary_plot_analysis')
            expr_fmt = expr.format(MEAN_ONLY, self.x_axis_col.lower())
        elif not rej_mean and rej_std:
            expr = gettext('seasonality_summary_plot_analysis')
            expr_fmt = expr.format(STD_ONLY, self.x_axis_col.lower())
        else:
            return None

        return expr_fmt
