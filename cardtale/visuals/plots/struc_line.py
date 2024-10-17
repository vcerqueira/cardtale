from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import gettext

from cardtale.core.data import TimeSeriesData
from cardtale.visuals.config import PLOT_NAMES


class SeriesLinePlot(Plot):
    HEIGHT = 4.5
    WIDTH = 12

    def __init__(self, tsd: TimeSeriesData, name: str):
        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.plot_name = PLOT_NAMES['struc_line']
        self.caption = gettext('series_line_plot_caption')
        self.show_me = True

    def build(self):
        self.plot = LinePlot.univariate(data=self.tsd.df,
                                        x_axis_col=self.tsd.time_col,
                                        y_axis_col=self.tsd.target_col,
                                        add_smooth=True)

    def analyse(self):
        range_analysis = \
            gettext('series_line_plot_analysis1').format(int(self.tsd.summary.stats['count']),
                                                         self.tsd.dt.frequency_name,
                                                         self.tsd.summary.dt_range[0],
                                                         self.tsd.summary.dt_range[1])

        stats_analysis = \
            gettext('series_line_plot_analysis2').format(self.tsd.summary.stats['mean'],
                                                         self.tsd.summary.stats['50%'],
                                                         self.tsd.summary.stats['std'],
                                                         self.tsd.summary.stats['min'],
                                                         self.tsd.summary.stats['max'])

        self.analysis.append(range_analysis)
        self.analysis.append(stats_analysis)
