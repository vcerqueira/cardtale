from cardtale.cards.analyser.base import ReportAnalyser
from cardtale.visuals.plots.trend_line import TrendLinePlot
from cardtale.visuals.plots.trend_dist import TrendDistPlots
from cardtale.data.uvts import UVTimeSeries


class TrendAnalysis(ReportAnalyser):

    def __init__(self, data: UVTimeSeries):
        super().__init__(data)

        components = self.data.decompose()
        self.data.df['Trend'] = components['Trend']

        self.plots = {
            'trend_line': TrendLinePlot(name='series_trend', data=self.data),
            'trend_dist': TrendDistPlots(name=['series_trend_dhist', 'series_trend_lagplot'], data=self.data),
        }

        self.metadata = {
            'section_header_str': 'trend_section_header',
            'section_intro_str': 'trend_section_intro',
        }
