import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

from cardtale.data.time_features import TimeDF
from cardtale.analytics.tsa.summary import SeriesSummary
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import SERIES, INDEX
from cardtale.data.config.frequency import AVAILABLE_FREQ
from cardtale.data.config.typing import Period
from cardtale.cards.strings import join_l

unq_freq_list = pd.Series([*AVAILABLE_FREQ.values()]).unique().tolist()

UNAVAILABLE_FREQUENCY_ERROR = f'Unknown or unavailable frequency. ' \
                              f'Please resample your data to one of the following frequencies: ' \
                              f'{join_l([*AVAILABLE_FREQ], "or")}. ' \
                              f'These refer to {join_l(unq_freq_list, "and")} sampling periods, respectively.'

ESTIMATED_PERIOD = 'Seasonal period was not provided. ' \
                   'This parameter was estimated to be: {}'

UNKNOWN_PERIOD = 'Unknown period'


class UVTimeSeries:
    """
    This is a data class for univariate time series

    Attributes:
        series (pd.Series): Univariate time series
        df (pd.DataFrame): Series as a pd.DF (index as column)
        period (Period): Main period of the data (e.g. 12 for monthly data)
        dt (TimeDF): Temporal information class object
        summary (SeriesSummary): summary stats of the series
        diff_summary (SeriesSummary): summary stats of the differenced series
        tests (TestingComponents): TestingComponents object with series tests
        verbose (bool): Whether to print status during process
    """

    def __init__(self,
                 series: pd.Series,
                 frequency: str,
                 period: Period = None,
                 verbose: bool = False):
        """
        Class constructor
        :param series: Univariate time series
        :param frequency: Sampling frequency of the data. Needs to be compatible with pandas
        :param period: Main period of the data (e.g. 12 for monthly data)
        """

        assert frequency in AVAILABLE_FREQ.keys(), \
            UNAVAILABLE_FREQUENCY_ERROR

        if not isinstance(series.index, pd.DatetimeIndex):
            series.index = pd.to_datetime(series.index)

        if self.series_is_int(series):
            series = series.astype(int)

        self.series = series
        self.series.index.name = INDEX
        self.series.name = SERIES
        self.df = series.reset_index()

        self.verbose = verbose

        self.dt = TimeDF(frequency)
        self.dt.setup(self.series)

        if period is not None:
            self.period = period
        else:
            self.period = self.dt.formats.loc[self.dt.frequency, 'main_period_int']
            if self.verbose:
                print(ESTIMATED_PERIOD.format(self.period))

        self.date_format = self.dt.formats['format_pretty'][self.dt.frequency]

        self.summary, self.diff_summary = \
            SeriesSummary(n_lags=self.period * 2), \
            SeriesSummary(n_lags=self.period * 2)

        self.summary.summarise(self.series, self.period, self.date_format)
        self.summary.fit_distributions(self.series)

        self.diff_summary.summarise(self.series.diff()[1:], self.period, self.date_format)
        self.diff_summary.fit_distributions(self.series.diff()[1:])

        self.tests = TestingComponents(self.series,
                                       self.dt.formats,
                                       period=self.period)

    def decompose(self, add_residuals: bool = False):
        ts_decomp = STL(self.series, period=self.period).fit()

        components = {
            'Trend': ts_decomp.trend,
            'Seasonal': ts_decomp.seasonal,
        }

        if add_residuals:
            components['Residuals'] = ts_decomp.resid

        components_df = pd.DataFrame(components).reset_index()

        return components_df

    def run_tests(self):
        seasonal_df = self.get_seasonal()
        self.tests.run(seasonal_df)

    def get_seasonal(self):
        return pd.concat([self.df, self.dt.recurrent], axis=1)

    def get_period_groups(self, grouping_period: str):
        seas_df = self.get_seasonal()

        assert grouping_period in seas_df, UNKNOWN_PERIOD

        data_groups = seas_df.groupby(seas_df[grouping_period])[SERIES]

        data_groups = {k: x.values for k, x in data_groups}

        return data_groups

    @staticmethod
    def series_is_int(series: pd.Series) -> bool:
        is_close = np.allclose(series, series.astype(int), equal_nan=True)

        return is_close
