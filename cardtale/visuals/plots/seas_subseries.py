from cardtale.visuals.plot import Plot
from cardtale.visuals.base.seasonal import SeasonalPlot
from cardtale.cards.strings import gettext
from cardtale.analytics.testing.card.seasonality import SeasonalityTesting

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
        """

        :param data:
        :param name:
        :param named_seasonality:
        :param x_axis_col:
        :param y_axis_col:
        :param tests_were_analysed: Whether statistical tests were already analysed in
        a previous plot. This happens if a seasonal line plot is shown before (for main period)
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

    def build(self):
        self.plot = SeasonalPlot.sub_series(data=self.tsd.seas_df,
                                            group_col=self.x_axis_col,
                                            x_axis_col=self.tsd.time_col,
                                            y_axis_col=self.y_axis_col)

    def analyse(self):
        freq_named = f'{self.x_axis_col}ly'


        show_plots, failed_periods = self.tests.seasonality.get_show_analysis()

        """
        show_plots={'Monthly': {'seas_subseries': {'show': False,
                                'which': {'by_perf': False, 'by_st': False}},
             'seas_summary': {'show': False}},
             'Quarterly': {'seas_subseries': {'show': True,
                                              'which': {'by_perf': True, 'by_st': False}},
                           'seas_summary': {'show': False}},
             'Yearly': {'seas_subseries': {'show': True,
                                           'which': {'by_perf': True, 'by_st': False}},
                        'seas_summary': {'show': True}}}
            
            freq_named='Monthly'
            freq_named='Monthly'
            
        
        """


        if show_plots[self.named_seasonality][self.plot_id]['show']:
            self.show_me = True
        else:
            return

        if not show_plots[freq_named]['seas_summary']['show']:
            groups_comps = gettext('seasonality_summary_fail').format(f'{self.x_axis_col.lower()}s')
            self.analysis.append(groups_comps)

        tests = self.tests.seasonality.tests[self.named_seasonality].tests

        named_level_st = self.tests.trend.prob_level_str

        if not self.tests_were_analysed:
            seas_str_analysis = SeasonalityTesting.seasonal_tests_parser(tests, freq_named.lower())
            self.analysis.append(seas_str_analysis)

        data_groups = self.tsd.get_period_groups(grouping_period=self.x_axis_col)

        within_groups_analysis = SeasonalityTesting.seasonal_subseries_st_parser(self.x_axis_col, data_groups,
                                                                                 named_level_st)
        self.analysis.append(within_groups_analysis)

        effect_analysis = SeasonalityTesting.seasonal_subseries_parser(show_plots,
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
