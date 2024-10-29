import numpy as np
import pandas as pd

from cardtale.core.time import TimeDF
from cardtale.analytics.operations.tsa.decomposition import get_stl_components
from cardtale.core.config.freq import AVAILABLE_FREQ
from cardtale.core.config.typing import Period
from cardtale.core.profile import SeriesProfile
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
        df (pd.DataFrame): Series as a pd.DF (index as column)
        period (Period): Main period of the data (e.g. 12 for monthly data)
        dt (TimeDF): Temporal information class object
        summary (SeriesSummary): summary stats of the series
        diff_summary (SeriesSummary): summary stats of the differenced series
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
        self.is_integer_valued = False

        self._assert_datatypes(df, freq)

        self.df = df
        self.dt = TimeDF(freq)
        self.dt.setup(self.df, self.time_col, self.target_col)
        self.seas_df = None
        self.stl_df = None
        self.name = ''

        if period is not None:
            self.period = period
        else:
            self.period = self.dt.formats.loc[self.dt.freq, 'main_period_int']

        self.date_format = self.dt.formats['format_pretty'][self.dt.freq]

        self.summary = SeriesProfile(n_lags=self.period * 2)
        self.diff_summary = SeriesProfile(n_lags=self.period * 2)

        self.setup()

    def setup(self):
        # done
        if self.ts_is_integer(self.df[self.target_col]):
            self.df[self.target_col] = self.df[self.target_col].astype(int)
            self.is_integer_valued = True
        else:
            self.is_integer_valued = False

        s = self.get_target_series(self.df, self.target_col, self.time_col)

        self.summary.run(s, self.period, self.date_format)
        self.diff_summary.run(s.diff()[1:], self.period, self.date_format)

        self.seas_df = pd.concat([self.df, self.dt.recurrent], axis=1)
        self.stl_df = get_stl_components(series=s, period=self.period)

        self.set_tsd_name()

    def set_tsd_name(self):
        self.name = self.df[self.id_col].values[0]

    def get_period_groups(self, grouping_period: str):
        # done... questions about self.target_col

        # remove ly from the period
        if grouping_period[-2:] == 'ly':
            grouping_period = grouping_period[:-2]

        assert grouping_period in self.seas_df, UNKNOWN_PERIOD

        data_groups = self.seas_df.groupby(self.seas_df[grouping_period], observed=False)[self.target_col]

        data_groups = {k: x.values for k, x in data_groups}

        return data_groups

    def _assert_datatypes(self, df: pd.DataFrame, freq: str):
        # done
        """
        :param df: Time series dataset
        :type df: pd.DataFrame

        :param freq: Sampling frequency
        :type freq: str
        """

        assert freq in AVAILABLE_FREQ.keys(), \
            UNAVAILABLE_FREQUENCY_ERROR

        assert pd.api.types.is_datetime64_any_dtype(df[self.time_col]), \
            "Column 'ds' must be of type pd.Timestamp"

    @staticmethod
    def ts_is_integer(series: pd.Series) -> bool:
        # done

        is_int = np.allclose(series, series.astype(int), equal_nan=True)

        return is_int

    @staticmethod
    def get_target_series(df, target_col, time_col):
        s = pd.Series(data=df[target_col].values, index=df[time_col], name=target_col)

        return s
