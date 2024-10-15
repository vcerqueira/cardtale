from typing import List

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.summary import SummaryStatPlot

from cardtale.cards.strings import gettext
from cardtale.data.utils.errors import AnalysisLogicalError, LOGICAL_ERROR_MSG
from cardtale.data.uvts import UVTimeSeries
from cardtale.visuals.config import SERIES, PLOT_NAMES

MEANS = 'eq_means'
SDEVS = 'eq_std'
MEAN_AND_STD = 'mean and standard deviation'
MEAN_ONLY = 'mean'
STD_ONLY = 'standard deviation'


class SeasonalSummaryPlots(Plot):

    def __init__(self,
                 data: UVTimeSeries,
                 name: List[str],
                 named_seasonality: str,
                 x_axis_col: str):
        super().__init__(data=data, multi_plot=True, name=name)

        self.plot_id = 'seas_summary'

        self.named_seasonality = named_seasonality
        self.caption = gettext('seasonality_summary_plot_caption')

        self.x_axis_col = x_axis_col

        self.caption_expr = f'{self.x_axis_col}ly'

        self.plot_name = PLOT_NAMES[self.plot_id]
        self.plot_name += f' ({self.x_axis_col}ly)'

    def build(self):

        seasonal_df = self.data.get_seasonal()

        mean_plot = SummaryStatPlot.SummaryPlot(data=seasonal_df,
                                                group_col=self.x_axis_col,
                                                y_col=SERIES,
                                                func='mean',
                                                y_lab='Mean')

        std_plot = SummaryStatPlot.SummaryPlot(data=seasonal_df,
                                               group_col=self.x_axis_col,
                                               y_col=SERIES,
                                               func='std',
                                               y_lab='Standard Deviation')

        self.plot = {'lhs': mean_plot, 'rhs': std_plot}

    def analyse(self):
        show_plots, failed_periods = self.data.tests.seasonality.get_show_analysis()

        if show_plots[self.named_seasonality][self.plot_id]['show']:
            self.show_me = True
        else:
            return

        tests = self.data.tests.seasonality.tests[self.named_seasonality]

        group_comparisions = tests.moments_bool

        rej_mean = group_comparisions[MEANS]
        rej_std = group_comparisions[SDEVS]

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
