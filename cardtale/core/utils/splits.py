from typing import List

import pandas as pd
from sklearn.model_selection import train_test_split

MAX_PARTITION_SIZE = 0.5
GQ_DEFAULT_NAMES = ['First', 'Last']
CHANGE_DEFAULT_NAMES = ['Before Change', 'After Change']


class DataSplit:
    """
    Class for splitting data into partitions.

    Methods:
        goldfeldquant_partition(residuals, partition_size, partition_names):
            Splits residuals into partitions for Goldfeld-Quandt test.
        change_partition(data, cp_index, partition_names, target_col, time_col, return_series):
            Splits data into partitions based on a change point index.
        df_var_to_categorical(df, variable):
            Converts a DataFrame variable to categorical type.
    """

    @staticmethod
    def goldfeldquant_partition(residuals: pd.Series,
                                partition_size: float,
                                partition_names: List[str] = GQ_DEFAULT_NAMES):
        """
        Splits residuals into partitions for Goldfeld-Quandt test.

        Args:
            residuals (pd.Series): Residuals to be partitioned.
            partition_size (float): Size of each partition as a fraction of the total.
            partition_names (List[str], optional): Names of the partitions. Defaults to GQ_DEFAULT_NAMES.

        Returns:
            pd.DataFrame: DataFrame with partitioned residuals.
        """

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
                         target_col: str = 'y',
                         time_col: str = 'ds',
                         return_series: bool = False):
        """
        Splits data into partitions based on a change point index.

        Args:
            data (pd.DataFrame): Data to be partitioned.
            cp_index (int): Index of the change point.
            partition_names (List[str], optional): Names of the partitions. Defaults to CHANGE_DEFAULT_NAMES.
            target_col (str, optional): Column name for the target variable. Defaults to 'y'.
            time_col (str, optional): Column name for the time variable. Defaults to 'ds'.
            return_series (bool, optional): Flag to return partitions as series. Defaults to False.

        Returns:
            pd.DataFrame or tuple: DataFrame with partitioned data or tuple of series if return_series is True.
        """

        Before, After = train_test_split(data, train_size=cp_index, shuffle=False)

        if return_series:
            return Before, After

        n_bf, n_af = Before.shape[0], After.shape[0]

        p1_df = pd.DataFrame({target_col: Before[target_col], time_col: range(n_bf)})
        p1_df['Part'] = partition_names[0]

        p2_df = pd.DataFrame({target_col: After[target_col], time_col: range(n_af)})
        p2_df['Part'] = partition_names[1]

        df = pd.concat([p1_df, p2_df])

        df['Part'] = cls.df_var_to_categorical(df, 'Part')

        return df

    @staticmethod
    def df_var_to_categorical(df: pd.DataFrame, variable: str):
        """
        Converts a DataFrame variable to categorical type.

        Args:
            df (pd.DataFrame): Input DataFrame.
            variable (str): Column name to be converted to categorical.

        Returns:
            pd.Categorical: Categorical variable.
        """

        assert variable in df.columns, 'Unknown column'

        unq_values = df[variable].unique()

        var_as_cat = pd.Categorical(df[variable], categories=unq_values)

        return var_as_cat
