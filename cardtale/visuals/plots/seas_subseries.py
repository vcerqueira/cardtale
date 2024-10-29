from cardtale.visuals.plot import Plot
from cardtale.visuals.base.seasonal import SeasonalPlot
from cardtale.cards.strings import gettext
from cardtale.cards.parsers.seasonality import SeasonalityTestsParser
from cardtale.cards.parsers.trend import TrendTestsParser

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import PLOT_NAMES

MEANS = 'eq_means'
SDEVS = 'eq_std'


class SeasonalSubSeriesPlot(Plot):

    def __init__(self,
                 tsd: TimeSeriesData,
                 tests: TestingComponents,
                 name: str,
                 named_seasonality: str,
                 x_axis_col: str,
                 y_axis_col: str,
                 tests_were_analysed: bool):

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

    def build(self):
        self.plot = SeasonalPlot.sub_series(data=self.tsd.seas_df,
                                            group_col=self.x_axis_col,
                                            x_axis_col=self.tsd.time_col,
                                            y_axis_col=self.y_axis_col)

    def analyse(self):
        freq_named = f'{self.x_axis_col}ly'

        show_plots, failed_periods = self.tests.seasonality.show_plots, self.tests.seasonality.failed_periods

        if show_plots[self.named_seasonality][self.plot_id]['show']:
            self.show_me = True
        else:
            return

        if not show_plots[freq_named]['seas_summary']['show']:
            groups_comps = gettext('seasonality_summary_fail').format(f'{self.x_axis_col.lower()}s')
            self.analysis.append(groups_comps)

        # tests = self.tests.seasonality.tests[self.named_seasonality].tests
        tests = self.tests.seasonality.get_tests_by_named_seasonality(self.named_seasonality)

        named_level_st = TrendTestsParser.parse_level_prob(self.tests.trend)
        # named_level_st = self.tests.trend.prob_level_str

        if not self.tests_were_analysed:
            seas_str_analysis = SeasonalityTestsParser.seasonal_tests_parser(tests, freq_named.lower())
            self.analysis.append(seas_str_analysis)

        g_trend = self.tests.seasonality.group_trends[f'{self.x_axis_col}ly']

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
        self.img_data['caption'] = self.img_data['caption'].format(plot_id, self.caption_expr.title(),
                                                                   self.caption_expr)
