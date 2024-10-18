from cardtale.cards.analyser.base import ReportAnalyser
from cardtale.visuals.plots.trend_line import TrendLinePlot
from cardtale.visuals.plots.trend_dist import TrendDistPlots
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents


class TrendAnalysis(ReportAnalyser):

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        super().__init__(tsd, tests)

        # todo do i need this assignment? surely not mate
        self.tsd.df['Trend'] = self.tsd.stl_df['Trend']

        self.plots = {
            'trend_line': TrendLinePlot(tsd=self.tsd, tests=self.tests, name='series_trend'),
            'trend_dist': TrendDistPlots(tsd=self.tsd,
                                         tests=self.tests,
                                         name=['series_trend_dhist', 'series_trend_lagplot']),
        }

        self.metadata = {
            'section_header_str': 'trend_section_header',
            'section_intro_str': 'trend_section_intro',
        }
