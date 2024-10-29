from cardtale.visuals.plot import Plot
from cardtale.visuals.base.seasonal import SeasonalPlot
from cardtale.cards.strings import join_l, gettext
from cardtale.analytics.testing.card.seasonality import SeasonalityTesting
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import PLOT_NAMES


class SeasonalLinePlot(Plot):

    def __init__(self,
                 tsd: TimeSeriesData,
                 tests: TestingComponents,
                 name: str,
                 add_labels: bool,
                 named_seasonality: str,
                 x_axis_col: str,
                 group_col: str):
        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.named_seasonality = named_seasonality
        self.caption = gettext('seasonality_line_month_year_caption')
        self.x_axis_col = x_axis_col
        self.group_col = group_col
        self.add_labels = add_labels

        self.caption_expr = f'{self.x_axis_col}ly', self.group_col

        self.plot_name = PLOT_NAMES['seas_line']
        self.plot_name += f' ({self.x_axis_col}ly)'

        self.tests = tests

    def build(self):
        self.plot = SeasonalPlot.lines(data=self.tsd.seas_df,
                                       x_axis_col=self.x_axis_col,
                                       y_axis_col=self.tsd.target_col,
                                       group_col=self.group_col,
                                       add_labels=self.add_labels,
                                       add_smooth=True)

    def analyse(self):
        """
        SeasonalLinePlot is always shown because it refers to the main period

        It also serves as the place to summarise the results for other periods
        (if no seasonality is found in those periods)
        """
        self.show_me = True

        # tests = self.tests.seasonality.tests[self.named_seasonality].tests
        tests = self.tests.seasonality.get_tests_by_named_seasonality(self.named_seasonality).tests

        main_freq = self.caption_expr[0]

        # print(tests)

        period = f'{self.group_col}ly'.lower()

        seas_str_analysis = SeasonalityTesting.seasonal_tests_parser(tests, period)
        # print('seas_str_analysis')
        self.analysis.append(seas_str_analysis)

        show_analysis, failed_periods = self.tests.seasonality.get_show_analysis()
        # print(show_analysis)

        self_perf = show_analysis[main_freq]['seas_subseries']['which']['by_perf']
        if self_perf:
            perf_analysis = gettext('seasonality_line_self_perf').format(main_freq.lower(), 'improves')
        else:
            perf_analysis = gettext('seasonality_line_self_perf').format(main_freq.lower(), 'decreases')

        self.analysis.append(perf_analysis)

        # which seasonal subseries plots will not be shown
        invalid_periods = [self.named_seasonality, f'{self.x_axis_col}ly']
        no_season_periods = failed_periods['seas_subseries']
        no_season_periods = [k for k in no_season_periods if k not in invalid_periods]

        # which summary plots will not be shown
        no_groupdiff_periods = failed_periods['seas_summary']
        no_groupdiff_periods = [k for k in no_groupdiff_periods if k != self.named_seasonality]
        no_groupdiff_periods = [k for k in no_groupdiff_periods if k in no_season_periods]

        if len(no_season_periods) > 0:
            # explain the outcome which led to the exclusion of the subseries plot
            seas_other_analysis = gettext('seasonality_line_analysis_other').format(join_l(no_season_periods))

            self.analysis.append(seas_other_analysis)

        if len(no_groupdiff_periods) > 0:
            # explain the outcome which led to the exclusion of the summary plot
            # in this case, I only show this here for the periods which also exclude subseries
            groups_comps = gettext('seasonality_summary_fail').format(f'{self.x_axis_col.lower()}s')
            self.analysis.append(groups_comps)

    def format_caption(self, plot_id: int):
        self.img_data['caption'] = \
            self.img_data['caption'].format(plot_id,
                                            self.caption_expr[0].lower(),
                                            self.caption_expr[1].lower())
