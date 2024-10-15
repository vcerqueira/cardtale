from cardtale.data.uvts import UVTimeSeries
from cardtale.cards.analyser.base import ReportAnalyser
from cardtale.visuals.plots.change_marking import ChangesMarksPlot
from cardtale.visuals.plots.change_dist import ChangeDistPlots


class ChangeAnalysis(ReportAnalyser):

    def __init__(self, data: UVTimeSeries):
        super().__init__(data=data)

        self.plots = {
            'marked_changes': ChangesMarksPlot(name='change_lines', data=data),
            'dist_changes': ChangeDistPlots(name=['parts_dist', 'parts_dens'], data=data),
        }

        self.marked_changes = None
        self.dist_changes = None

        self.metadata = {
            'section_header_str': 'change_section_header',
            'section_intro_str': 'change_section_intro',
        }
