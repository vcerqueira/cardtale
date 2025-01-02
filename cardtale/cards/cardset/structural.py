from cardtale.visuals.plots.struc_line import SeriesLinePlot
from cardtale.visuals.plots.struc_components import SeriesComponentsPlot
from cardtale.visuals.plots.struc_acf import SeriesACFPlot
from cardtale.visuals.plots.struc_pacf import SeriesPACFPlot
from cardtale.cards.cardset.base import Card
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents


class StructuralCard(Card):
    """
    Class for analyzing structural components of a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        tests (TestingComponents): Testing components for the time series data.
        plots (dict): Dictionary of Plot objects for structural analysis.
        metadata (dict): Metadata for the card.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        """
        Initializes the StructuralCard with the given time series data and testing components.

        Args:
            tsd (TimeSeriesData): Time series data object.
            tests (TestingComponents): Testing components for the time series data.
        """

        super().__init__(tsd, tests)

        self.plots = {
            'line_plot': SeriesLinePlot(tsd=tsd, name='series_plot'),
            # 'dist_plot': SeriesDistPlots(tsd=tsd, name=['hist_plot', 'boxplot_plot']),
            'comp_plot': SeriesComponentsPlot(tsd=tsd, tests=tests, name='components_plot'),
            'acf_plot': SeriesACFPlot(tsd=tsd, name='acf_plot'),
            'pacf_plot': SeriesPACFPlot(tsd=tsd, name='pacf_plot'),
        }

        self.metadata = {
            'section_id': 'structural',
            'section_header_str': 'structural_section_header',
            'section_intro_str': 'structural_section_intro',
            'section_toc_success': 'structural_toc_success',
        }
