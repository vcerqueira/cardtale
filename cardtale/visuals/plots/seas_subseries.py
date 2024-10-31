from typing import Optional

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.seasonal import SeasonalPlot
from cardtale.cards.parsers.trend import TrendTestsParser

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import PLOT_NAMES
from cardtale.cards.strings import join_l, gettext


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

        show_plots = self.tests.seasonality.show_plots

        if show_plots[self.named_seasonality][self.plot_id]['show']:
            self.show_me = True
        else:
            return

        plt_deq1 = self.deq_group_differences_aux()
        plt_deq2 = self.deq_seasonality_stationarity()
        plt_deq3 = self.deq_seasonality_trend()
        plt_deq4 = self.deq_seasonality_impact()

        self.analysis = [plt_deq1, plt_deq2, plt_deq3, plt_deq4]
        self.analysis = [x for x in self.analysis if x is not None]

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

    def deq_seasonality_stationarity(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Is the time series stationary in seasonality for the given period?

        Approach:
            - Statistical tests
        """

        freq_named = 'Daily' if self.x_axis_col == 'Day' else f'{self.x_axis_col}ly'

        tests = self.tests.seasonality.get_tests_by_named_seasonality(self.named_seasonality).tests

        all_tests = tests.index.tolist()
        rej_tests = tests[tests > 0].index.tolist()
        not_rej_tests = tests[tests < 1].index.tolist()

        if self.tests_were_analysed:
            return None

        if all(tests > 0):
            expr = gettext('seasonality_line_analysis_seas_all1')
            expr_fmt = expr.format(join_l(all_tests), freq_named)
        elif all(tests < 1):
            expr = gettext('seasonality_line_analysis_seas_all0')
            expr_fmt = expr.format(join_l(all_tests), freq_named)
        else:
            expr = gettext('seasonality_line_analysis_seas_mix')
            expr_fmt = expr.format(freq_named, join_l(rej_tests), join_l(not_rej_tests))

        return expr_fmt

    def deq_seasonality_trend(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Is there a trend within seasonal periods of the time series?

        Approach:
            - Statistical tests
        """

        freq_named = 'Daily' if self.x_axis_col == 'Day' else f'{self.x_axis_col}ly'

        if freq_named not in self.tests.seasonality.group_trends:
            return None

        prob = self.tests.trend.prob_level

        if prob < 0.3:
            named_level_st = 'no evidence'
        elif prob < 0.6:
            named_level_st = 'a slight evidence'
        elif prob < 0.9:
            named_level_st = 'a reasonable evidence'
        else:
            named_level_st = 'a strong evidence'

        g_trend = self.tests.seasonality.group_trends[freq_named]

        if named_level_st == 'no evidence':
            preprend = 'But, within'
            emphasis = ''
        else:
            preprend = 'Within'
            emphasis = ' also'

        perc_within = 100 * (g_trend > 0.6).mean()
        perc_within_str = f'{int(perc_within)}%'
        if perc_within_str == '100%':
            perc_within_str = 'all'
        elif perc_within_str == '0%':
            perc_within_str = 'none'

        expr_fmt1 = gettext('seasonality_subseries_group1').format(named_level_st)
        if named_level_st == 'no evidence':
            if perc_within_str == 'none':
                expr_fmt2 = gettext('seasonality_subseries_group2bothnone').format(self.x_axis_col)
                expr_fmt = f'{expr_fmt1} {expr_fmt2}'
                return expr_fmt
        else:
            if perc_within_str == 'none':
                expr_fmt2 = gettext('seasonality_subseries_group2none').format(self.x_axis_col)
                expr_fmt = f'{expr_fmt1} {expr_fmt2}'
                return expr_fmt

        expr2 = gettext('seasonality_subseries_group2')
        expr_fmt2 = expr2.format(preprend, emphasis, perc_within_str, self.x_axis_col)

        expr_fmt = f'{expr_fmt1} {expr_fmt2}'

        return expr_fmt

    def deq_seasonality_impact(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Is there a trend within seasonal periods of the time series?

        Approach:
            - Statistical tests
        """

        show_plots = self.tests.seasonality.show_plots

        freq_named = 'Daily' if self.x_axis_col == 'Day' else f'{self.x_axis_col}ly'

        by_st = show_plots[self.named_seasonality]['seas_subseries']['which']['by_st']
        by_perf = show_plots[freq_named]['seas_subseries']['which']['by_perf']

        if not by_st and not by_perf:
            self.show_me = False
            return None

        if not by_st and by_perf:
            expr = gettext('seasonality_subseries_opt1')
        elif by_st and not by_perf:
            expr = gettext('seasonality_subseries_opt2')
        else:
            expr = gettext('seasonality_subseries_opt3')

        expr_fmt = expr.format(self.named_seasonality.lower())

        return expr_fmt
