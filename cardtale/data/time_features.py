import re
from typing import Tuple

import numpy as np
import pandas as pd

from cardtale.data.config.frequency import FREQ_TAB, FREQUENCIES, PERIOD_DF, SEASONS
from cardtale.data.utils.categories import as_categorical
from cardtale.visuals.config import PERIOD, FREQ_NAME, SERIES

DFTuple = Tuple[pd.DataFrame, pd.DataFrame]

N_MONTHS = 12
SEASON_LEN = 3
CATEGORICAL_COLUMNS = ['Month', 'Weekday', 'Quarter']

INDEX_NOT_DT_ERROR = 'Input variable "index" must be a pd.DatetimeIndex object'


class TimeDF:
    """
    todo check greykit features:     - https://github.com/linkedin/greykite/blob/master/greykite/common/features/timeseries_features.py
    todo check gluonts features: https://ts.gluon.ai/stable/api/gluonts/gluonts.time_feature.html
    """

    def __init__(self, frequency: str):
        self.frequency = frequency
        self.formats = None
        self.sequence = None
        self.recurrent = None
        self.frequency_name = ''

    def setup(self, series: pd.Series):
        index = series.index

        assert isinstance(index, pd.DatetimeIndex), INDEX_NOT_DT_ERROR

        self.formats = self.get_granularities(self.frequency)

        valid_periods = self.get_periods(self.frequency)
        valid_periods.name = PERIOD

        self.formats = pd.concat([self.formats, valid_periods], axis=1)
        self.formats.fillna(1, inplace=True)
        self.formats[PERIOD] = self.formats[PERIOD].astype(int)

        self.sequence, self.recurrent = self.get_frequency_set(index)

        self.recurrent = pd.concat([self.recurrent,
                                    self.get_averages(series)], axis=1)

        self.frequency_name = self.formats.loc[self.frequency][FREQ_NAME].lower()

    def get_averages(self, series: pd.Series):
        """
        Computing the average for each sequential period
        e.g. Quarter averages
        """
        freqs = self.formats['name'].values[1:].tolist()
        freqs = [re.sub('ly$', '', x) for x in freqs]

        avg_df = pd.DataFrame(index=series.index)

        df = self.sequence.copy()
        df[SERIES] = series.values

        for freq_ in freqs:
            avg_df[f'{freq_} Average'] = df.groupby([freq_])[SERIES].transform(lambda x: x.mean()).values

        avg_df.reset_index(drop=True, inplace=True)

        return avg_df

    @classmethod
    def get_frequency_set(cls, index: pd.DatetimeIndex) -> DFTuple:
        """
        todo I can subset this info by frequency, but I don't think it help in any major way
        """
        forward_freq = {
            'Year': index.to_period('Y'),
            'Quarter': index.to_period('Q'),
            'Month': index.to_period('M'),
            'Week': index.to_period('W'),
            'Day': index.to_period('D'),
            'Hour': index.to_period('H'),
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
            recurrent_df[col] = as_categorical(recurrent_df, col)

        n_unq = recurrent_df.nunique()

        recurrent_df = recurrent_df[n_unq[n_unq > 1].index.tolist()]

        return forward_df, recurrent_df

    @staticmethod
    def get_granularities(frequency: str):
        """
        :param frequency: Data sampling frequency (pandas compatible)

        :return All frequencies "above" the input frequency
        """

        idx = np.argwhere([x == frequency for x in FREQUENCIES])[0][0]

        valid_freq = FREQ_TAB[idx:]

        return valid_freq

    @staticmethod
    def get_periods(frequency: str):
        all_periods = PERIOD_DF[frequency]
        valid_periods = all_periods[all_periods > 0]

        return valid_periods

    @staticmethod
    def get_seasons(index: pd.DatetimeIndex):
        season_ = index.month % N_MONTHS // SEASON_LEN + 1
        season_.name = 'season'

        season_df = pd.DataFrame(season_).replace({'season': SEASONS})

        season_f = season_df['season']

        return season_f
