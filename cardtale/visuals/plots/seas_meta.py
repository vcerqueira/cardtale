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

        self.plots = self._frequency_plots()[self.tsd.dt.freq_name.lower()]

        self.make_all()

        return self.plots

    def make_all(self):

        for k in self.plots:
            print(k)
            self.plots[k].analyse()

        self.plots = {k: self.plots[k] for k in self.plots
                      if self.plots[k].show_me}

        for k in self.plots:
            self.plots[k].build()
            self.plots[k].save()

    def _frequency_plots(self):

        plots = {

            'hourly': {
                'daily_line': SeasonalLinePlot(tsd=self.tsd,
                                               tests=self.tests,
                                               name='daily_line',
                                               add_labels=False,
                                               named_seasonality='Daily',
                                               group_col='Day',
                                               x_axis_col='Hour'),
                'daily_sseries': SeasonalSubSeriesPlot(tsd=self.tsd,
                                                       tests=self.tests,
                                                       name='daily_sseries',
                                                       named_seasonality='Daily',
                                                       x_axis_col='Hour',
                                                       y_axis_col=self.tsd.target_col,
                                                       tests_were_analysed=True),
                'daily_summary': SeasonalSummaryPlots(tsd=self.tsd,
                                                      tests=self.tests,
                                                      name=['daily_meanp', 'daily_stdp'],
                                                      x_axis_col='Hour',
                                                      named_seasonality='Hourly'),
                'weekly_sseries': SeasonalSubSeriesPlot(tsd=self.tsd,
                                                        tests=self.tests,
                                                        name='weekly_sseries',
                                                        named_seasonality='Weekly',
                                                        x_axis_col='Week',
                                                        y_axis_col='Week Average',
                                                        tests_were_analysed=False),
                'weekly_summary': SeasonalSummaryPlots(tsd=self.tsd,
                                                       tests=self.tests,
                                                       name=['weekly_meanp', 'weekly_stdp'],
                                                       x_axis_col='Week',
                                                       named_seasonality='Weekly'),
            },
            'daily': {
                'weekly_line': SeasonalLinePlot(tsd=self.tsd,
                                                tests=self.tests,
                                                name='weekly_line',
                                                add_labels=False,
                                                named_seasonality='Weekly',
                                                group_col='Week',
                                                x_axis_col='Day'),
                'weekly_sseries': SeasonalSubSeriesPlot(tsd=self.tsd,
                                                        tests=self.tests,
                                                        name='weekly_sseries',
                                                        named_seasonality='Weekly',
                                                        x_axis_col='Day',
                                                        y_axis_col=self.tsd.target_col,
                                                        tests_were_analysed=True),
                'weekly_summary': SeasonalSummaryPlots(tsd=self.tsd,
                                                       tests=self.tests,
                                                       name=['weekly_meanp', 'weekly_stdp'],
                                                       x_axis_col='Day',
                                                       named_seasonality='Daily'),
                'monthly_sseries': SeasonalSubSeriesPlot(tsd=self.tsd,
                                                         tests=self.tests,
                                                         name='monthly_sseries',
                                                         named_seasonality='Monthly',
                                                         x_axis_col='Month',
                                                         y_axis_col='Month Average',
                                                         tests_were_analysed=False),
                'monthly_summary': SeasonalSummaryPlots(tsd=self.tsd,
                                                        tests=self.tests,
                                                        name=['monthly_meanp', 'monthly_stdp'],
                                                        x_axis_col='Month',
                                                        named_seasonality='Monthly'),

            },

            'weekly': {

                'yearly_line': SeasonalLinePlot(tsd=self.tsd,
                                                tests=self.tests,
                                                name='yearly_line',
                                                add_labels=True,
                                                named_seasonality='Yearly',
                                                group_col='Year',
                                                x_axis_col='Week'),
                'yearly_sseries': SeasonalSubSeriesPlot(tsd=self.tsd,
                                                        tests=self.tests,
                                                        name='yearly_sseries',
                                                        named_seasonality='Yearly',
                                                        x_axis_col='Week',
                                                        y_axis_col=self.tsd.target_col,
                                                        tests_were_analysed=True),
                'yearly_summary': SeasonalSummaryPlots(tsd=self.tsd,
                                                       tests=self.tests,
                                                       name=['yearly_meanp', 'yearly_stdp'],
                                                       x_axis_col='Week',
                                                       named_seasonality='Weekly'),
                'monthly_sseries': SeasonalSubSeriesPlot(tsd=self.tsd,
                                                         tests=self.tests,
                                                         name='monthly_sseries',
                                                         named_seasonality='Monthly',
                                                         x_axis_col='Month',
                                                         y_axis_col='Month Average',
                                                         tests_were_analysed=False),
                'monthly_summary': SeasonalSummaryPlots(tsd=self.tsd,
                                                        tests=self.tests,
                                                        name=['monthly_meanp', 'monthly_stdp'],
                                                        x_axis_col='Month',
                                                        named_seasonality='Monthly'),

            },

            'monthly': {
                'yearly_line': SeasonalLinePlot(tsd=self.tsd,
                                                tests=self.tests,
                                                name='yearly_line',
                                                add_labels=True,
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
            },

            'quarterly': {
                'yearly_line': SeasonalLinePlot(tsd=self.tsd,
                                                tests=self.tests,
                                                name='yearly_line',
                                                add_labels=True,
                                                named_seasonality='Yearly',
                                                group_col='Year',
                                                x_axis_col='Quarter'),
                'yearly_sseries': SeasonalSubSeriesPlot(tsd=self.tsd,
                                                        tests=self.tests,
                                                        name='yearly_sseries',
                                                        named_seasonality='Yearly',
                                                        x_axis_col='Quarter',
                                                        y_axis_col=self.tsd.target_col,
                                                        tests_were_analysed=True),
                'yearly_summary': SeasonalSummaryPlots(tsd=self.tsd,
                                                       tests=self.tests,
                                                       name=['yearly_meanp', 'yearly_stdp'],
                                                       x_axis_col='Quarter',
                                                       named_seasonality='Quarterly'),
            },

            'yearly': None,

        }

        return plots
