from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import gettext

from cardtale.data.uvts import UVTimeSeries
from cardtale.visuals.config import PLOT_NAMES


class SeriesLinePlot(Plot):

    def __init__(self, name: str, data: UVTimeSeries):
        super().__init__(data=data,multi_plot=False, name=name)

        self.caption = gettext('series_line_plot_caption')
        self.show_me = True

        self.plot_name = PLOT_NAMES['struc_line']
        self.height = 4.5
        self.width = 12

    def build(self):
        self.plot = LinePlot.univariate(data=self.data.df,
                                        x_axis_col='Index',
                                        y_axis_col='Series',
                                        add_smooth=True)

    def analyse(self):
        range_analysis = \
            gettext('series_line_plot_analysis1').format(int(self.data.summary.stats['count']),
                                                         self.data.dt.frequency_name,
                                                         self.data.summary.dt_range[0],
                                                         self.data.summary.dt_range[1])

        stats_analysis = \
            gettext('series_line_plot_analysis2').format(self.data.summary.stats['mean'],
                                                         self.data.summary.stats['50%'],
                                                         self.data.summary.stats['std'],
                                                         self.data.summary.stats['min'],
                                                         self.data.summary.stats['max'])

        self.analysis.append(range_analysis)
        self.analysis.append(stats_analysis)
