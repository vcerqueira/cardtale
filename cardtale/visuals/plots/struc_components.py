from typing import Optional

from cardtale.core.data import TimeSeriesData
from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import gettext, join_l
from cardtale.analytics.testing.base import TestingComponents

from cardtale.core.config.analysis import DECOMPOSITION_METHOD, DECOMPOSITION_METHOD_SHORT


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
        self.plot_name = 'Trend, Seasonality, and Residuals'

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

        freq = self.tsd.dt.freq_longly

        self.img_data['caption'] = self.img_data['caption'].format(plot_id, freq, DECOMPOSITION_METHOD)

    def deq_trend_component(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Is there a strong trend component in the time series?

        Approach:
            - Decomposition analysis
        """

        trend, no_trend, _, _ = self.tests.trend.results_in_list()

        expr0 = gettext('series_components_analysis_trend_str')
        expr_fmt0 = expr0.format(self.tests.trend.trend_strength)

        if len(no_trend) == 0:
            expr = gettext('series_components_analysis_trend_all1')
            expr_fmt = expr.format(join_l(trend))
        elif len(trend) == 0:
            expr = gettext('series_components_analysis_trend_all0')
            expr_fmt = expr.format(join_l(no_trend))
        else:
            expr = gettext('series_components_analysis_trend_mix')
            expr_fmt = expr.format(join_l(trend), join_l(no_trend))

        expr_fmt = expr_fmt0 + expr_fmt

        return expr_fmt

    def deq_seasonal_component(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Is there a strong seasonal component in the time series?

        Approach:
            - Decomposition analysis
        """

        expr0 = gettext('series_components_analysis_seas_str')
        expr_fmt0 = expr0.format(self.tests.seasonality.seasonal_strength)

        seas_t = self.tests.seasonality.seas_tests_on_main

        main_freq_longly = self.tsd.dt.formats.loc[self.tsd.dt.freq_short, 'main_period_name'][0]

        if all(seas_t > 0):
            expr = gettext('series_components_analysis_seas_all1')
            expr_fmt = expr.format(join_l(seas_t.index))
        elif all(seas_t < 1):
            expr = gettext('series_components_analysis_seas_all0')
            expr_fmt = expr.format(join_l(seas_t.index))
        else:
            expr = gettext('series_components_analysis_seas_mix')

            rej_tests = seas_t[seas_t > 0].index.tolist()
            not_rej_tests = seas_t[seas_t < 1].index.tolist()
            conclusion = 'seasonal unit root' if rej_tests[0] == 'OCSB' else 'strong seasonality'

            expr_fmt = expr.format(freq_longly=main_freq_longly,
                                   test1=rej_tests[0],
                                   test1_conclusion=conclusion,
                                   test2=not_rej_tests[0])

        expr_fmt = expr_fmt0 + expr_fmt

        return expr_fmt

    def deq_residuals_component(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): What is the structure of the residuals based on an STL decomposition?

        Approach:
            - Decomposition analysis
        """

        resid_str = self.tsd.stl_resid_str

        expr = gettext('series_components_resid_symmetry')
        expr_fmt = expr.format(DECOMPOSITION_METHOD_SHORT,
                               resid_str['behaviour'],
                               resid_str['positive_pct'],
                               resid_str['negative_pct'],
                               resid_str['pos_mean'],
                               resid_str['neg_mean'])

        if not resid_str['auto_corr_exists'].any():
            expr2 = gettext('series_components_resid_auto_corr_ind')
        else:
            expr2 = gettext('series_components_resid_auto_corr')

        expr_fmt2 = expr2.format(self.tsd.period)

        expr_fmt += expr_fmt2

        return expr_fmt
