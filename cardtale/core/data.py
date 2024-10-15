import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL


from cardtale.core.time import TimeDF
from cardtale.core.config.freq import AVAILABLE_FREQ
from cardtale.core.config.typing import Period
from cardtale.core.profile import SeriesProfile
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.config import SERIES, INDEX
from cardtale.cards.strings import join_l

unq_freq_list = pd.Series([*AVAILABLE_FREQ.values()]).unique().tolist()

UNAVAILABLE_FREQUENCY_ERROR = f'Unknown or unavailable frequency. ' \
                              f'Please resample your data to one of the following frequencies: ' \
                              f'{join_l([*AVAILABLE_FREQ], "or")}. ' \
                              f'These refer to {join_l(unq_freq_list, "and")} sampling periods, respectively.'

ESTIMATED_PERIOD = 'Seasonal period was not provided. ' \
                   'This parameter was estimated to be: {}'

UNKNOWN_PERIOD = 'Unknown period'


class TimeSeriesData:
    """ TimeSeriesData

    Time series dataset following a Nixtla-based structure

    #todo review docstrings
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
                 df: pd.DataFrame,
                 freq: str,
                 id_col: str = 'unique_id',
                 time_col: str = 'ds',
                 target_col: str = 'y',
                 period: Period = None):
        """
        :param df: Time series dataset following a nixtla-based structure
        :type df: pd.DataFrame

        :param freq: Sampling frequency of the data. Needs to be compatible with pandas
        :param freq: str

        :param id_col: Column name that for the time series identifier.
        For single time series, id_col will be a constant value
        :type id_col: str

        :param time_col: Column name for the time variable
        :type time_col: str

        :param target_col: Column name for the target variable
        :type target_col: str

        :param period: Main period of the data (e.g. 12 for monthly data), in case multiple seasonality can be present
        :type period: int
        """

        self.id_col = id_col
        self.time_col = time_col
        self.target_col = target_col

        assert freq in AVAILABLE_FREQ.keys(), \
            UNAVAILABLE_FREQUENCY_ERROR

        assert pd.api.types.is_datetime64_any_dtype(df[self.time_col]), \
            "Column 'ds' must be of type pd.Timestamp"

        if self.ts_is_integer(df[self.target_col]):
            df[self.target_col] = df[self.target_col].astype(int)

        self.df = df

        self.dt = TimeDF(freq)
        self.dt.setup(self.series)

        if period is not None:
            self.period = period
        else:
            self.period = self.dt.formats.loc[self.dt.frequency, 'main_period_int']

        self.date_format = self.dt.formats['format_pretty'][self.dt.frequency]

        self.summary, self.diff_summary = \
            SeriesProfile(n_lags=self.period * 2), \
            SeriesProfile(n_lags=self.period * 2)

        self.summary.summarise(self.series, self.period, self.date_format)
        self.summary.fit_distributions(self.series)

        self.diff_summary.summarise(self.series.diff()[1:], self.period, self.date_format)
        self.diff_summary.fit_distributions(self.series.diff()[1:])

        self.tests = TestingComponents(self.series, self.dt.formats, period=self.period)

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
    def ts_is_integer(series: pd.Series) -> bool:
        is_int = np.allclose(series, series.astype(int), equal_nan=True)

        return is_int
