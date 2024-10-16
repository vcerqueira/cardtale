from typing import List

import pandas as pd
from sklearn.model_selection import train_test_split

from cardtale.visuals.config import SERIES

MAX_PARTITION_SIZE = 0.5
GQ_DEFAULT_NAMES = ['First', 'Last']
CHANGE_DEFAULT_NAMES = ['Before Change', 'After Change']


class DataSplit:

    @staticmethod
    def goldfeldquant_partition(residuals: pd.Series,
                                partition_size: float,
                                partition_names: List[str] = GQ_DEFAULT_NAMES):
        assert partition_size < MAX_PARTITION_SIZE

        n = residuals.shape[0]

        p1 = residuals.head(int(n * partition_size))
        p2 = residuals.tail(int(n * partition_size))

        p1_df = pd.DataFrame({'Residuals': p1, 'Id': range(len(p1))})
        p1_df['Part'] = partition_names[0]

        p2_df = pd.DataFrame({'Residuals': p2, 'Id': range(len(p2))})
        p2_df['Part'] = partition_names[1]

        df = pd.concat([p1_df, p2_df])

        return df

    @classmethod
    def change_partition(cls,
                         data: pd.DataFrame,
                         cp_index: int,
                         partition_names: List[str] = CHANGE_DEFAULT_NAMES,
                         return_series: bool = False):
        """

        :param return_series:
        :param data: Data from UVTimeseries
        :param cp_index: first change point index from katsing
        :param partition_names:
        :return:
        """

        Before, After = train_test_split(data, train_size=cp_index, shuffle=False)

        if return_series:
            return Before[SERIES], After[SERIES]

        n_bf, n_af = Before.shape[0], After.shape[0]

        p1_df = pd.DataFrame({'Series': Before['Series'], 'Id': range(n_bf)})
        p1_df['Part'] = partition_names[0]

        p2_df = pd.DataFrame({'Series': After['Series'], 'Id': range(n_af)})
        p2_df['Part'] = partition_names[1]

        df = pd.concat([p1_df, p2_df])

        df['Part'] = cls.df_var_to_categorical(df, 'Part')

        return df

    @staticmethod
    def df_var_to_categorical(df: pd.DataFrame, variable: str):
        assert variable in df.columns, 'Unknown column'

        unq_values = df[variable].unique()

        var_as_cat = pd.Categorical(df[variable], categories=unq_values)

        return var_as_cat

