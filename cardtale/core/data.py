import numpy as np
import pandas as pd

from cardtale.core.time import TimeDF
from cardtale.analytics.operations.tsa.decomposition import DecompositionSTL
from cardtale.core.config.freq import AVAILABLE_FREQ
from cardtale.core.config.typing import Period
from cardtale.core.profile import SeriesProfile
from cardtale.cards.strings import join_l

unq_freq_list = pd.Series([*AVAILABLE_FREQ.values()]).unique().tolist()

UNAVAILABLE_FREQUENCY_ERROR = f'Unknown or unavailable frequency. ' \
                              f'Please resample your data to one of the following frequencies: ' \
                              f'{join_l([*AVAILABLE_FREQ], "or")}. ' \
                              f'These refer to {join_l(unq_freq_list, "and")} ' \
                              f'sampling periods, respectively.'

ESTIMATED_PERIOD = 'Seasonal period was not provided. ' \
                   'This parameter was estimated to be: {}'

UNKNOWN_PERIOD = 'Unknown period'


class TimeSeriesData:
    """
    TimeSeriesData

    Time series dataset following a Nixtla-based structure.

    Attributes:
        df (pd.DataFrame): Series as a pd.DF (index as column)
        period (Period): Main period of the data (e.g. 12 for monthly data)
        dt (TimeDF): Temporal information class object
        summary (SeriesSummary): Summary stats of the series
        diff_summary (SeriesSummary): Summary stats of the differenced series
        id_col (str): Column name for the time series identifier
        time_col (str): Column name for the time variable
        target_col (str): Column name for the target variable
        is_integer_valued (bool): Flag indicating if the series is integer-valued
        seas_df (pd.DataFrame): DataFrame with seasonal information
        stl_df (pd.DataFrame): DataFrame with STL decomposition components
        name (str): Name of the time series
    """

    def __init__(self,
                 df: pd.DataFrame,
                 freq: str,
                 id_col: str = 'unique_id',
                 time_col: str = 'ds',
                 target_col: str = 'y',
                 period: Period = None):
        """
        Initializes the TimeSeriesData class.

        Args:
            df (pd.DataFrame): Time series dataset following a Nixtla-based structure.
            freq (str): Sampling frequency of the data. Needs to be compatible with pandas.

            id_col (str, optional): Column name for the time series identifier.
            Defaults to 'unique_id'.

            time_col (str, optional): Column name for the time variable.
            Defaults to 'ds'.

            target_col (str, optional): Column name for the target variable.
            Defaults to 'y'.

            period (Period, optional): Main period of the data (e.g. 12 for monthly data).
            Defaults to None.
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
        self.stl_resid_str = None
        self.name = ''

        if period is not None:
            self.period = period
        else:
            self.period = self.dt.formats.loc[self.dt.freq_short, 'main_period_int']

        self.date_format = self.dt.formats['format_pretty'][self.dt.freq_short]

        self.summary = SeriesProfile(n_lags=self.period * 2)
        self.diff_summary = SeriesProfile(n_lags=self.period * 2)

        self.setup()

    def setup(self):
        """
        Sets up the time series data by running summary statistics and STL decomposition.
        """

        if self.ts_is_integer(self.df[self.target_col]):
            self.df[self.target_col] = self.df[self.target_col].astype(int)
            self.is_integer_valued = True
        else:
            self.is_integer_valued = False

        s = self.get_target_series(self.df, self.target_col, self.time_col)

        self.summary.run(s, self.period, self.date_format)
        self.diff_summary.run(s.diff()[1:], self.period, self.date_format)

        self.seas_df = pd.concat([self.df, self.dt.recurrent], axis=1)
        self.stl_df = DecompositionSTL.get_stl_components(series=s, period=self.period)
        self.stl_resid_str = DecompositionSTL.residuals_ljung_box(self.stl_df['Residuals'], n_lags=self.period)

        self.set_tsd_name()

    def set_tsd_name(self):
        """
        Sets the name of the time series data.
        """

        self.name = self.df[self.id_col].values[0]

    def get_period_groups(self, grouping_period: str):
        """
        Gets the period groups based on the specified grouping period.

        Args:
            grouping_period (str): Grouping period (e.g., 'monthly', 'weekly').

        Returns:
            dict: Dictionary containing the period groups.

        Raises:
            AssertionError: If the grouping period is unknown.
        """

        # remove ly from the period
        if grouping_period[-2:] == 'ly':
            grouping_period = grouping_period[:-2]

        assert grouping_period in self.seas_df, UNKNOWN_PERIOD

        data_groups = self.seas_df.groupby(self.seas_df[grouping_period], observed=False)[self.target_col]

        data_groups = {k: x.values for k, x in data_groups}

        return data_groups

    def _assert_datatypes(self, df: pd.DataFrame, freq: str):
        assert freq in AVAILABLE_FREQ, \
            UNAVAILABLE_FREQUENCY_ERROR

        assert pd.api.types.is_datetime64_any_dtype(df[self.time_col]), \
            "Column 'ds' must be of type pd.Timestamp"

    @staticmethod
    def ts_is_integer(series: pd.Series) -> bool:
        """
        Checks if the series is integer-valued.

        Args:
            series (pd.Series): Input series.

        Returns:
            bool: True if the series is integer-valued, False otherwise.
        """

        is_int = np.allclose(series, series.astype(int), equal_nan=True)

        return is_int

    @staticmethod
    def get_target_series(df, target_col, time_col):
        """
        Gets the target series from the DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame.
            target_col (str): Column name for the target variable.
            time_col (str): Column name for the time variable.

        Returns:
            pd.Series: Target series.
        """

        s = pd.Series(data=df[target_col].values, index=df[time_col], name=target_col)

        return s
