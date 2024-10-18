from cardtale.visuals.plots.var_dist import VarianceDistPlots
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.cards.analyser.base import ReportAnalyser


class VarianceAnalysis(ReportAnalyser):

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        super().__init__(tsd, tests)

        self.plots = {
            'var_dist': VarianceDistPlots(tsd=self.tsd,
                                          tests=self.tests,
                                          name=['residuals_dist', 'series_part_dist'])
        }

        self.metadata = {
            'section_header_str': 'variance_section_header',
            'section_intro_str': 'variance_section_intro',
        }
