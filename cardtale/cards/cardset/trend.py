import pandas as pd

from cardtale.cards.cardset.base import Card
from cardtale.visuals.plots.trend_line import TrendLinePlot
from cardtale.visuals.plots.trend_dist import TrendDistPlots
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents

pd.options.mode.chained_assignment = None


class TrendCard(Card):
    """
    Class for analyzing trend components in a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        tests (TestingComponents): Testing components for the time series data.
        plots (dict): Dictionary of Plot objects for trend analysis.
        metadata (dict): Metadata for the card.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        """
        Initializes the TrendCard with the given time series data and testing components.

        Args:
            tsd (TimeSeriesData): Time series data object.
            tests (TestingComponents): Testing components for the time series data.
        """

        super().__init__(tsd, tests)

        self.plots = {
            'trend_line': TrendLinePlot(tsd=self.tsd, tests=self.tests, name='series_trend'),
            'trend_dist': TrendDistPlots(tsd=self.tsd,
                                         tests=self.tests,
                                         name=['series_trend_dhist', 'series_trend_lagplot']),
        }

        self.metadata = {
            'section_id': 'trend',
            'section_header_str': 'trend_section_header',
            'section_intro_str': 'trend_section_intro',
            'section_toc_success': 'trend_toc_success',
            'section_toc_failure': 'trend_toc_failure',
        }
