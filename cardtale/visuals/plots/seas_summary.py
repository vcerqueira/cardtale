from typing import List

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.summary import SummaryStatPlot

from cardtale.cards.strings import gettext
from cardtale.core.utils.errors import AnalysisLogicalError, LOGICAL_ERROR_MSG
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import PLOT_NAMES

MEAN_AND_STD = 'mean and standard deviation'
MEAN_ONLY = 'mean'
STD_ONLY = 'standard deviation'


class SeasonalSummaryPlots(Plot):

    def __init__(self,
                 tsd: TimeSeriesData,
                 tests: TestingComponents,
                 name: List[str],
                 named_seasonality: str,
                 x_axis_col: str):
        super().__init__(tsd=tsd, multi_plot=True, name=name)

        self.plot_id = 'seas_summary'

        self.named_seasonality = named_seasonality
        self.caption = gettext('seasonality_summary_plot_caption')

        self.x_axis_col = x_axis_col

        self.caption_expr = f'{self.x_axis_col}ly'

        self.plot_name = PLOT_NAMES[self.plot_id]
        self.plot_name += f' ({self.x_axis_col}ly)'

        self.tests = tests

    def build(self):

        mean_plot = SummaryStatPlot.SummaryPlot(data=self.tsd.seas_df,
                                                group_col=self.x_axis_col,
                                                y_col=self.tsd.target_col,
                                                func='mean',
                                                y_lab='Mean')

        std_plot = SummaryStatPlot.SummaryPlot(data=self.tsd.seas_df,
                                               group_col=self.x_axis_col,
                                               y_col=self.tsd.target_col,
                                               func='std',
                                               y_lab='Standard Deviation')

        self.plot = {'lhs': mean_plot, 'rhs': std_plot}

    def analyse(self):
        show_plots, failed_periods = self.tests.seasonality.show_plots, self.tests.seasonality.failed_periods

        if show_plots[self.named_seasonality][self.plot_id]['show']:
            self.show_me = True
        else:
            return

        tests = self.tests.seasonality.get_tests_by_named_seasonality(self.named_seasonality)

        group_tests = tests.group_tests_b
        rej_mean, rej_std = group_tests['eq_means'], group_tests['eq_std']

        if rej_mean and rej_std:
            summary_an = gettext('seasonality_summary_plot_analysis')
            summary_an = summary_an.format(MEAN_AND_STD, self.x_axis_col.lower())
        elif rej_mean and not rej_std:
            summary_an = gettext('seasonality_summary_plot_analysis')
            summary_an = summary_an.format(MEAN_ONLY, self.x_axis_col.lower())
        elif not rej_mean and rej_std:
            summary_an = gettext('seasonality_summary_plot_analysis')
            summary_an = summary_an.format(STD_ONLY, self.x_axis_col.lower())
        else:
            raise AnalysisLogicalError(LOGICAL_ERROR_MSG)

        self.analysis.append(summary_an)

    def format_caption(self, plot_id: int):
        self.img_data['caption'] = \
            self.img_data['caption'].format(plot_id, self.caption_expr.lower())
