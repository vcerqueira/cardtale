from cardtale.visuals.plots.var_dist import VarianceDistPlots
from cardtale.data.uvts import UVTimeSeries
from cardtale.cards.analyser.base import ReportAnalyser


class VarianceAnalysis(ReportAnalyser):

    def __init__(self, data: UVTimeSeries):
        super().__init__(data)

        self.data = data

        self.plots = {
            'var_dist': VarianceDistPlots(name=['residuals_dist', 'series_part_dist'],
                                          data=self.data)
        }

        self.metadata = {
            'section_header_str': 'variance_section_header',
            'section_intro_str': 'variance_section_intro',
        }
