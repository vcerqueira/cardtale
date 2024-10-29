from cardtale.cards.cardset.base import Card
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.plots.seas_meta import SeasonalMetaPlots


class SeasonalityCard(Card):

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        super().__init__(tsd, tests)

        self.plots = {}
        self.meta_plot = None

        self.metadata = {
            'section_id': 'seasonality',
            'section_header_str': 'seasonality_section_header',
            'section_intro_str': 'seasonality_section_intro',
            'section_toc_success': 'seasonality_toc_success',
            'section_toc_failure': 'seasonality_toc_failure',
        }

        self.set_toc_content()

    def analyse(self):
        if self.tsd.dt.freq_name == 'Yearly':
            self.show_content = False
            return

        pass

    def build_plots(self):
        self.meta_plot = SeasonalMetaPlots(tsd=self.tsd, tests=self.tests)

        self.plots = self.meta_plot.make_plots()
