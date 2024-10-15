from cardtale.visuals.plot import Plot
from cardtale.visuals.base.line_plots import LinePlot
from cardtale.cards.strings import gettext

from cardtale.data.uvts import UVTimeSeries
from cardtale.visuals.config import PLOT_NAMES


class SeriesNonStationarityZonesPlot(Plot):

    def __init__(self, name: str, data: UVTimeSeries):
        super().__init__(data=data, multi_plot=False, name=name)

        self.caption = gettext('series_line_plot_caption')
        self.plot_name = PLOT_NAMES['struc_ns_zone']

    def build(self):
        segments_df, _ = self.data.summary.ns_zones

        self.plot = LinePlot.univariate_with_h_segments(data=self.data.df,
                                                        segments_data=segments_df,
                                                        x_axis_col='Index',
                                                        y_axis_col='Series')

    def analyse(self):
        segments_df, applied_diff = self.data.summary.ns_zones

        if segments_df.shape[0] < 1:
            return
        else:
            self.show_me = True

        nszone_analysis = gettext('series_ns_zone_analysis')

        self.analysis.append(nszone_analysis)
