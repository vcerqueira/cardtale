from cardtale.visuals.plots.var_dist import VarianceDistPlots
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.cards.cardset.base import Card


class VarianceCard(Card):

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        super().__init__(tsd, tests)

        self.plots = {
            'var_dist': VarianceDistPlots(tsd=self.tsd,
                                          tests=self.tests,
                                          name=['residuals_dist', 'series_part_dist'])
        }

        self.metadata = {
            'section_id': 'variance',
            'section_header_str': 'variance_section_header',
            'section_intro_str': 'variance_section_intro',
            'section_toc_success': 'variance_toc_success',
            'section_toc_failure': 'variance_toc_failure',
        }
