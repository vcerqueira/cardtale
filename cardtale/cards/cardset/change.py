from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.cards.cardset.base import Card
from cardtale.visuals.plots.change_marking import ChangesMarksPlot
from cardtale.visuals.plots.change_effect import ChangeEffectPlots


class ChangePointCard(Card):
    """
    Class for analyzing change points in a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        tests (TestingComponents): Testing components for the time series data.
        plots (dict): Dictionary of Plot objects for change points.
        marked_changes (ChangesMarksPlot): Plot object for marked changes.
        dist_changes (ChangeDistPlots): Plot object for distribution of changes.
        metadata (dict): Metadata for the card.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        """
        Initializes the ChangePointCard with the given time series data and testing components.

        Args:
            tsd (TimeSeriesData): Time series data object.
            tests (TestingComponents): Testing components for the time series data.
        """

        super().__init__(tsd=tsd, tests=tests)

        self.plots = {
            'marked_changes': ChangesMarksPlot(tsd=self.tsd, tests=self.tests, name='change_lines'),
            'change_effect': ChangeEffectPlots(tsd=self.tsd, tests=self.tests, name='change_effect'),
        }

        self.metadata = {
            'section_id': 'change_detection',
            'section_header_str': 'change_section_header',
            'section_intro_str': 'change_section_intro',
            'section_toc_success': 'change_toc_success',
            'section_toc_failure': 'change_toc_failure',
        }
