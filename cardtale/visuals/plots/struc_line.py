from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import gettext

from cardtale.core.data import TimeSeriesData
from cardtale.visuals.config import PLOT_NAMES


class SeriesLinePlot(Plot):
    """
    Class for creating and analyzing time series line plots.

    Attributes:
        HEIGHT (float): Default height for the plot.
        WIDTH (float): Default width for the plot.
        plot_name (str): Name of the plot.
        caption (str): Caption for the plot.
        show_me (bool): Flag indicating if the plot should be shown.
    """

    HEIGHT = 4.5
    WIDTH = 12

    def __init__(self, tsd: TimeSeriesData, name: str):
        """
        Initializes the SeriesLinePlot class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            name (str): Name of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.plot_name = PLOT_NAMES['struc_line']
        self.caption = gettext('series_line_plot_caption')
        self.show_me = True

    def build(self):
        """
        Creates the time series line plot.
        """

        self.plot = LinePlot.univariate(data=self.tsd.df,
                                        x_axis_col=self.tsd.time_col,
                                        y_axis_col=self.tsd.target_col,
                                        add_smooth=True)

    def analyse(self):
        """
        Analyzes the time series line plot.

        The analysis includes summarizing the data range and basic statistics.
        """

        range_analysis = \
            gettext('series_line_plot_analysis1').format(int(self.tsd.summary.stats['count']),
                                                         self.tsd.dt.freq_name,
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
