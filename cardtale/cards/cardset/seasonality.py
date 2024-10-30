from cardtale.cards.cardset.base import Card
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.plots.seas_meta import SeasonalMetaPlots


class SeasonalityCard(Card):
    """
    Class for analyzing seasonality in a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        tests (TestingComponents): Testing components for the time series data.
        plots (dict): Dictionary of Plot objects for seasonality.
        meta_plot (SeasonalMetaPlots): Plot object for seasonal metadata.
        metadata (dict): Metadata for the card.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        """
        Initializes the SeasonalityCard with the given time series data and testing components.

        Args:
            tsd (TimeSeriesData): Time series data object.
            tests (TestingComponents): Testing components for the time series data.
        """

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
        """
        Analyzes the time series data for seasonality.

        If the frequency of the time series data is 'Yearly', the content will not be shown.
        """

        if self.tsd.dt.freq_name == 'Yearly':
            self.show_content = False

    def build_plots(self):
        """
        Builds the plots for seasonality analysis.

        Creates a SeasonalMetaPlots object and generates the plots.
        """

        self.meta_plot = SeasonalMetaPlots(tsd=self.tsd, tests=self.tests)

        self.plots = self.meta_plot.make_plots()
