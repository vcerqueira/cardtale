from cardtale.cards.analyser.base import ReportAnalyser
from cardtale.data.uvts import UVTimeSeries
from cardtale.visuals.plots.seas_meta import SeasonalMetaPlots


class SeasonalityAnalysis(ReportAnalyser):

    def __init__(self, data: UVTimeSeries):
        super().__init__(data)

        self.plots = {}
        self.meta_plot = None

        self.metadata = {
            'section_header_str': 'seasonality_section_header',
            'section_intro_str': 'seasonality_section_intro',
        }

    def analyse(self):
        pass

    def build_plots(self, plot_dir=None):

        self.meta_plot = SeasonalMetaPlots(data=self.data)

        self.plots = self.meta_plot.make_plots(plot_dir)
