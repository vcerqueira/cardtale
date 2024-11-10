from typing import List, Union, Optional

import pandas as pd
from sklearn.model_selection import train_test_split

MAX_PARTITION_SIZE = 0.5
GQ_DEFAULT_NAMES = ['First', 'Last']
CHANGE_DEFAULT_NAMES = ['Before Change', 'After Change']

PandasObj = Union[pd.DataFrame, pd.Series]


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
    def goldfeldquant_partition(residuals: PandasObj,
                                partition_size: float,
                                partition_names: Optional[List[str]] = None):
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

        if partition_names is None:
            partition_names = GQ_DEFAULT_NAMES

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
                         data: PandasObj,
                         cp_index: int,
                         partition_names: Optional[List[str]] = None,
                         target_col: str = 'y',
                         time_col: str = 'ds',
                         return_data: bool = False):
        """
        Splits data into partitions based on a change point index.

        Args:
            data (pd.DataFrame): Data to be partitioned.
            cp_index (int): Index of the change point.
            partition_names (List[str], optional): Names of the partitions. Defaults to CHANGE_DEFAULT_NAMES.
            target_col (str, optional): Column name for the target variable. Defaults to 'y'.
            time_col (str, optional): Column name for the time variable. Defaults to 'ds'.
            return_data (bool, optional): Flag to return partitions as series. Defaults to False.

        Returns:
            pd.DataFrame or tuple: DataFrame with partitioned data or tuple of series if return_series is True.
        """

        if partition_names is None:
            partition_names = CHANGE_DEFAULT_NAMES

        before, after = train_test_split(data, train_size=cp_index, shuffle=False)

        if return_data:
            return before, after

        n_bf, n_af = before.shape[0], after.shape[0]

        p1_df = pd.DataFrame({target_col: before[target_col], time_col: range(n_bf)})
        p1_df['Part'] = partition_names[0]

        p2_df = pd.DataFrame({target_col: after[target_col], time_col: range(n_af)})
        p2_df['Part'] = partition_names[1]

        df = pd.concat([p1_df, p2_df])

        df['Part'] = cls.df_var_to_categorical(df, 'Part')

        return df

    @staticmethod
    def df_var_to_categorical(df: pd.DataFrame, variable: str, categories: Optional[List[str]] = None):
        """
        Converts a DataFrame variable to categorical type.

        Args:
            df (pd.DataFrame): Input DataFrame.
            variable (str): Column name to be converted to categorical.
            categories (str): Unique categories

        Returns:
            pd.Categorical: Categorical variable.
        """

        assert variable in df.columns, 'Unknown column'

        if categories is None:
            categories = df[variable].unique()

        var_as_cat = pd.Categorical(df[variable], categories=categories)

        return var_as_cat
