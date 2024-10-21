import re
from typing import Tuple

import numpy as np
import pandas as pd

from cardtale.core.config.freq import FREQ_TAB, FREQUENCIES, FREQ_INT_DF, SEASONS
from cardtale.core.utils.splits import DataSplit

DFTuple = Tuple[pd.DataFrame, pd.DataFrame]

N_MONTHS = 12
SEASON_LEN = 3
CATEGORICAL_COLUMNS = ['Month', 'Weekday', 'Quarter']


class TimeDF:
    """ TimeDF

    Time features dataset

    todo check greykit features: https://github.com/linkedin/greykite/blob/master/greykite/common/features/timeseries_features.py
    todo check gluonts features: https://ts.gluon.ai/stable/api/gluonts/gluonts.time_feature.html
    """

    def __init__(self, freq: str):
        """
        :param freq: Sampling frequency of the time series
        :type freq: str, pandas compatible
        """
        self.freq = freq
        self.formats = None
        self.sequence = None
        self.recurrent = None
        self.freq_name = ''

    def setup(self, df: pd.DataFrame, time_col: str, target_col: str):
        """

        Setup the time features dataset

        :param df: Time series dataset
        :type df: pd.DataFrame

        :param time_col: Column name denoting the temporal variable:
        :type time_col: str, for a column of pd.Timestamp-like type

        :param target_col: Column name denoting the numeric target variable
        :type target_col: str
        """
        self.set_formats()

        idx = df[[time_col]].set_index(time_col).index

        self.sequence, self.recurrent = self.get_freq_set(idx)

        s = pd.Series(data=df[target_col], index=df[time_col], name=target_col)
        freq_avg = self.get_freq_averages(s)

        self.recurrent = pd.concat([self.recurrent, freq_avg], axis=1)

    def set_formats(self):
        """
        Preparing frequency table
        """
        valid_periods = self.get_valid_int_freqs(self.freq)

        self.formats = self.get_freqs(self.freq)
        self.formats = pd.concat([self.formats, valid_periods], axis=1)
        self.formats.fillna(1, inplace=True)
        self.formats['period'] = self.formats['period'].astype(int)
        self.freq_name = self.formats.loc[self.freq]['name'].lower()

    def get_freq_averages(self, series: pd.Series):
        """

        Computing the average for each sequential period
        e.g. Quarter averages

        :param series: Univariate time series as pd.Series with a pd.DateTimeIndex index
        :type series: pd.Series with a pd.DateTimeIndex index
        """
        freqs = self.formats['name'].values[1:].tolist()
        freqs = [re.sub('ly$', '', x) for x in freqs]

        avg_df = pd.DataFrame(index=series.index)

        df = self.sequence.copy()
        df[series.name] = series.values

        for freq_ in freqs:
            avg_df[f'{freq_} Average'] = df.groupby([freq_])[series.name].transform(lambda x: x.mean()).values

        avg_df.reset_index(drop=True, inplace=True)

        return avg_df

    @classmethod
    def get_freq_set(cls, index: pd.DatetimeIndex) -> DFTuple:
        """
        todo I can subset this info by frequency, but I don't think it help in any major way
        """

        assert isinstance(index, pd.DatetimeIndex)

        forward_freq = {
            'Year': index.to_period('Y'),
            'Quarter': index.to_period('Q'),
            'Month': index.to_period('M'),
            'Week': index.to_period('W'),
            'Day': index.to_period('D'),
            'Hour': index.to_period('h'),
        }

        recurrent_freq = {
            'Season': cls.get_seasons(index),
            'Year': index.year,
            'Quarter': [f'Q{i}' for i in index.quarter],
            'Month Number': index.month,
            'Month': [x[:3] for x in index.month_name()],
            'Week': index.isocalendar().week.values,
            'Weekday': index.day_name(),
            'Day': index.day,
            'Hour': index.hour,
        }

        forward_df = pd.DataFrame(forward_freq)
        recurrent_df = pd.DataFrame(recurrent_freq)

        for col in CATEGORICAL_COLUMNS:
            recurrent_df[col] = DataSplit.df_var_to_categorical(recurrent_df, col)

        n_unq = recurrent_df.nunique()

        recurrent_df = recurrent_df[n_unq[n_unq > 1].index.tolist()]

        return forward_df, recurrent_df

    @staticmethod
    def get_freqs(frequency: str):
        """
        :param frequency: Data sampling frequency (pandas compatible)

        :return All frequencies "above" the input frequency
        """

        idx = np.argwhere([x == frequency for x in FREQUENCIES])[0][0]

        valid_freq = FREQ_TAB[idx:]

        return valid_freq

    @staticmethod
    def get_valid_int_freqs(freq: str):
        """ get_valid_freqs

        Get valid periods for the respective frequency. For example, monthly data can have 4 (quarter), or 12 (year)

        :param freq: Sampling frequency
        :type freq: str
        """
        all_periods = FREQ_INT_DF[freq]
        valid_periods = all_periods[all_periods > 0]
        valid_periods.name = 'period'

        return valid_periods

    @staticmethod
    def get_seasons(index: pd.DatetimeIndex):
        season_ = index.month % N_MONTHS // SEASON_LEN + 1
        season_.name = 'season'

        season_df = pd.DataFrame(season_).replace({'season': SEASONS})

        season_f = season_df['season']

        return season_f
