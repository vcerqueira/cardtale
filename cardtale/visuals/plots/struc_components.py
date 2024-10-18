from cardtale.core.data import TimeSeriesData
from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import gettext, join_l
from cardtale.analytics.testing.base import TestingComponents

from cardtale.core.config.analysis import DECOMPOSITION_METHOD
from cardtale.visuals.config import PLOT_NAMES


class SeriesComponentsPlot(Plot):

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: str):
        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.caption = gettext('series_components_caption')
        self.show_me = True
        self.plot_name = PLOT_NAMES['struc_components']

        self.tests = tests

    def build(self):
        self.plot = LinePlot.multivariate_grid(data=self.tsd.stl_df, scales='free')

    def analyse(self):

        seas_t = self.tests.seasonality.period_tests.tests
        # todo level not used
        trend, no_trend, level, no_level = self.tests.trend.results_in_list()

        if len(no_trend) == 0:
            trend_str_anl = gettext('series_components_analysis_trend_all1')
            trend_str_anl = trend_str_anl.format(join_l(trend))
        elif len(trend) == 0:
            trend_str_anl = gettext('series_components_analysis_trend_all0')
            trend_str_anl = trend_str_anl.format(join_l(no_trend))
        else:
            trend_str_anl = gettext('series_components_analysis_trend_mix')
            trend_str_anl = trend_str_anl.format(join_l(trend), join_l(no_trend))

        if all(seas_t > 0):
            seas_str_anl = gettext('series_components_analysis_seas_all1')
            seas_str_anl = seas_str_anl.format(join_l(seas_t.index))
        elif all(seas_t < 1):
            seas_str_anl = gettext('series_components_analysis_seas_all0')
            seas_str_anl = seas_str_anl.format(join_l(seas_t.index))
        else:
            seas_str_anl = gettext('series_components_analysis_seas_mix')
            seas_str_anl = seas_str_anl.format(join_l(seas_t[seas_t > 0].index),
                                               join_l(seas_t[seas_t < 1].index))

        self.analysis.append(trend_str_anl)
        self.analysis.append(seas_str_anl)

    def format_caption(self, plot_id: int):
        self.img_data['caption'] = self.img_data['caption'].format(plot_id, DECOMPOSITION_METHOD)
