import numpy as np
import pandas as pd

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import join_l, gettext
from cardtale.analytics.testing.components.trend import TrendShowTests

from cardtale.data.uvts import UVTimeSeries
from cardtale.visuals.config import INDEX, PLOT_NAMES
from cardtale.data.config.analysis import TREND_STRENGTH_INTERVAL


class TrendLinePlot(Plot):

    def __init__(self, name: str, data: UVTimeSeries):
        super().__init__(data=data, multi_plot=False, name=name)

        self.caption = gettext('trend_line_plot_caption')

        self.plot_name = PLOT_NAMES['trend_line']

    def build(self):
        self.plot = LinePlot.univariate_w_support(data=self.data.df,
                                                  x_axis_col=INDEX,
                                                  y_axis_col_main='Trend',
                                                  y_axis_col_supp='Series')

    def analyse(self):
        tests = self.data.tests.trend

        self.show_me, show_results = TrendShowTests.show_distribution_plot(tests)

        if not self.show_me:
            return

        time_corr_avg = tests.time_model.time_corr_avg
        corr_side = tests.time_model.side

        trend, no_trend, level, no_level = tests.results_in_list()

        dt = pd.Series(TREND_STRENGTH_INTERVAL) - np.abs(time_corr_avg)
        trend_label = dt[dt < 0].index[0]

        trend_analysis = gettext('trend_line_analysis1').format(join_l(trend))
        trend_analysis += gettext('trend_line_analysis2').format(trend_label, corr_side)
        self.analysis.append(trend_analysis)

        if len(no_trend) > 0:
            if len(no_trend) == 1:
                suffix = ''
            else:
                suffix = 's'

            no_trend_methods = gettext('trend_line_analysis3').format(suffix, join_l(no_trend))
            self.analysis.append(no_trend_methods)

        if len(level) > 0:
            lvl_anls = gettext('trend_line_analysis4').format(join_l(level))

            if len(no_level) > 0:
                lvl_anls += gettext('trend_line_analysis4ifany').format(join_l(no_level))
        else:
            lvl_anls = gettext('trend_line_analysis4none')

        self.analysis.append(lvl_anls)

        self.analysis.append(tests.parse_t_performance())
