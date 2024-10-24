from cardtale.visuals.plot import Plot
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import gettext
from cardtale.visuals.config import PLOT_NAMES


class ChangesMarksPlot(Plot):

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: str):
        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.caption = gettext('change_line_plot_caption')
        self.plot_name = PLOT_NAMES['change_marking']

        self.tests = tests

    def build(self):

        if self.show_me:
            cp, cp_idx = self.tests.change.get_change_points()

            self.plot = \
                LinePlot.univariate_change(data=self.tsd.df,
                                           x_axis_col=self.tsd.time_col,
                                           y_axis_col=self.tsd.target_col,
                                           change_points=cp_idx)

    def analyse(self):
        cp, cp_idx = self.tests.change.get_change_points()

        n_cp = len(cp)

        if n_cp > 0:
            self.show_me = True
            first_cp = cp[0]
            # if first_cp.direction == 'increase':
            #     cp_direction = 'increasing'
            # else:
            #     cp_direction = 'decreasing'

            if self.tests.change.level_increased:
                cp_direction = 'increasing'
            else:
                cp_direction = 'decreasing'

            cp_time = cp_idx[0].strftime(self.tsd.date_format)

            if n_cp == 1:
                n_anls = gettext('change_line_1point')
                prefix = ''
            else:
                n_anls = gettext('change_line_npoints').format(n_cp)
                prefix = 'first '

            self.analysis.append(n_anls)

            marked_analysis_first = gettext('change_line_analysis').format(prefix, cp_time, cp_direction)

            self.analysis.append(marked_analysis_first)

    def format_caption(self, plot_id: int):
        self.img_data['caption'] = \
            self.img_data['caption'].format(plot_id, self.tests.change.method)
