from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.cards.cardset.base import Card
from cardtale.visuals.plots.change_marking import ChangesMarksPlot
from cardtale.visuals.plots.change_dist import ChangeDistPlots


class ChangePointCard(Card):

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        super().__init__(tsd=tsd, tests=tests)

        self.plots = {
            'marked_changes': ChangesMarksPlot(tsd=self.tsd, tests=self.tests, name='change_lines'),
            'dist_changes': ChangeDistPlots(tsd=self.tsd, tests=self.tests, name=['parts_dist', 'parts_dens']),
        }

        self.marked_changes = None
        self.dist_changes = None

        self.metadata = {
            'section_header_str': 'change_section_header',
            'section_intro_str': 'change_section_intro',
        }
