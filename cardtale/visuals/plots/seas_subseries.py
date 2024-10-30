from typing import Optional

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.seasonal import SeasonalPlot
from cardtale.cards.strings import gettext
from cardtale.cards.parsers.seasonality import SeasonalityTestsParser
from cardtale.cards.parsers.trend import TrendTestsParser

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import PLOT_NAMES


class SeasonalSubSeriesPlot(Plot):
    """
    Class for creating and analyzing seasonal subseries plots.

    Attributes:
        tests_were_analysed (bool): Flag indicating if tests were already analyzed.
        caption (str): Caption for the plot.
        x_axis_col (str): Column name for the x-axis.
        y_axis_col (str): Column name for the y-axis.
        named_seasonality (str): Named seasonality for the plot.
        caption_expr (str): Expression for the caption.
        plot_id (str): Identifier for the plot.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for seasonality.
    """

    def __init__(self,
                 tsd: TimeSeriesData,
                 tests: TestingComponents,
                 name: str,
                 named_seasonality: str,
                 x_axis_col: str,
                 y_axis_col: str,
                 tests_were_analysed: bool):
        """
        Initializes the SeasonalSubSeriesPlot class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for seasonality.
            name (str): Name of the plot.
            named_seasonality (str): Named seasonality for the plot.
            x_axis_col (str): Column name for the x-axis.
            y_axis_col (str): Column name for the y-axis.
            tests_were_analysed (bool): Flag indicating if tests were already analyzed.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.tests_were_analysed = tests_were_analysed

        self.caption = gettext('seasonality_subseries_caption')
        self.x_axis_col = x_axis_col
        self.y_axis_col = y_axis_col
        self.named_seasonality = named_seasonality

        self.caption_expr = f'{self.x_axis_col}ly'.lower()

        self.plot_id = 'seas_subseries'

        self.plot_name = PLOT_NAMES[self.plot_id]
        self.plot_name += f' ({self.x_axis_col}ly)'

        self.tests = tests

    def build(self, *args, **kwargs):
        """
        Creates the seasonal subseries plot.
        """

        self.plot = SeasonalPlot.sub_series(data=self.tsd.seas_df,
                                            group_col=self.x_axis_col,
                                            x_axis_col=self.tsd.time_col,
                                            y_axis_col=self.y_axis_col)

    def analyse(self, *args, **kwargs):
        """
        Analyzes the seasonal subseries plot.

        The analysis includes checking for seasonality and summarizing the results.
        """

        if self.x_axis_col == 'Day':
            freq_named = 'Daily'
        else:
            freq_named = f'{self.x_axis_col}ly'

        self.deq_group_differences_aux()

        show_plots = self.tests.seasonality.show_plots

        if show_plots[self.named_seasonality][self.plot_id]['show']:
            self.show_me = True
        else:
            return

        tests = self.tests.seasonality.get_tests_by_named_seasonality(self.named_seasonality).tests

        named_level_st = TrendTestsParser.parse_level_prob(self.tests.trend)

        if not self.tests_were_analysed:
            seas_str_analysis = SeasonalityTestsParser.seasonal_tests_parser(tests, freq_named.lower())
            self.analysis.append(seas_str_analysis)

        if freq_named in self.tests.seasonality.group_trends:
            g_trend = self.tests.seasonality.group_trends[freq_named]
            within_groups_analysis = SeasonalityTestsParser.subseries_tests_parser(self.x_axis_col,
                                                                                   g_trend,
                                                                                   named_level_st)
            self.analysis.append(within_groups_analysis)

        effect_analysis = SeasonalityTestsParser.seasonal_subseries_parser(show_plots,
                                                                           st_freq=self.named_seasonality,
                                                                           lm_freq=freq_named)

        if effect_analysis is not None:
            self.analysis.append(effect_analysis)
        else:
            self.show_me = False
            return

    def format_caption(self, plot_id: int):
        """
        Formats the caption with the respective number and method.

        Args:
            plot_id (int): Plot id.
        """

        self.img_data['caption'] = self.img_data['caption'].format(plot_id, self.caption_expr.title(),
                                                                   self.caption_expr)

    def deq_group_differences_aux(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Are there statistical differences in the time series groups?

        Approach:
            - anova_test
            - kruskal_test
            - levene_test
            - bartlett_test
        """

        if self.x_axis_col == 'Day':
            freq_named = 'Daily'
        else:
            freq_named = f'{self.x_axis_col}ly'

        show_plots = self.tests.seasonality.show_plots

        if not show_plots[freq_named]['seas_summary']['show']:
            expr = gettext('seasonality_summary_fail')
            expr_fmt = expr.format(self.x_axis_col.lower())
        else:
            expr_fmt = None

        return expr_fmt
