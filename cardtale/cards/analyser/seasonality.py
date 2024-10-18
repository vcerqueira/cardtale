from cardtale.cards.analyser.base import ReportAnalyser
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.plots.seas_meta import SeasonalMetaPlots


class SeasonalityAnalysis(ReportAnalyser):

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        super().__init__(tsd, tests)

        self.plots = {}
        self.meta_plot = None

        self.metadata = {
            'section_header_str': 'seasonality_section_header',
            'section_intro_str': 'seasonality_section_intro',
        }

    def analyse(self):
        pass

    def build_plots(self):
        self.meta_plot = SeasonalMetaPlots(tsd=self.tsd, tests=self.tests)

        self.plots = self.meta_plot.make_plots()
