import logging

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.plots.seas_line import SeasonalLinePlot
from cardtale.visuals.plots.seas_subseries import SeasonalSubSeriesPlot
from cardtale.visuals.plots.seas_summary import SeasonalSummaryPlots

logging.getLogger('matplotlib').setLevel(logging.ERROR)


class SeasonalMetaPlots:

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        self.tsd = tsd
        self.tests = tests

        self.plots = {}

    def make_plots(self):
        """
        todo abstract this to other frequencies
        """

        self.plots = {
            'yearly_line': SeasonalLinePlot(tsd=self.tsd,
                                            tests=self.tests,
                                            name='yearly_line',
                                            named_seasonality='Yearly',
                                            group_col='Year',
                                            x_axis_col='Month'),
            'yearly_sseries': SeasonalSubSeriesPlot(tsd=self.tsd,
                                                    tests=self.tests,
                                                    name='yearly_sseries',
                                                    named_seasonality='Yearly',
                                                    x_axis_col='Month',
                                                    y_axis_col=self.tsd.target_col,
                                                    tests_were_analysed=True),
            'yearly_summary': SeasonalSummaryPlots(tsd=self.tsd,
                                                   tests=self.tests,
                                                   name=['yearly_meanp', 'yearly_stdp'],
                                                   x_axis_col='Month',
                                                   named_seasonality='Monthly'),
            'quarterly_sseries': SeasonalSubSeriesPlot(tsd=self.tsd,
                                                       tests=self.tests,
                                                       name='quarterly_sseries',
                                                       named_seasonality='Quarterly',
                                                       x_axis_col='Quarter',
                                                       y_axis_col='Quarter Average',
                                                       tests_were_analysed=False),
            'quarterly_summary': SeasonalSummaryPlots(tsd=self.tsd,
                                                      tests=self.tests,
                                                      name=['quarterly_meanp', 'quarterly_stdp'],
                                                      x_axis_col='Quarter',
                                                      named_seasonality='Quarterly'),
        }

        self.make_all()

        return self.plots

    def make_all(self):

        for k in self.plots:
            # print(k)
            self.plots[k].analyse()

        self.plots = {k: self.plots[k] for k in self.plots
                      if self.plots[k].show_me}

        for k in self.plots:
            self.plots[k].build()
            self.plots[k].save()

    def _frequency_plots(self):

        plots = {
            'half_hourly': {

            },

            'hourly': {

            },

            'daily': {

            },

            'weekly': {

            },

            'monthly': {

            },

            'quarterly': {

            },

            'yearly': {

            },

        }

        return plots
