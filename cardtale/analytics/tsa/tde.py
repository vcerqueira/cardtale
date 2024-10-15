from typing import Tuple, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from cardtale.data.config.landmarks import SHUFFLE


class TimeDelayEmbedding:
    """
    This is a class for applying time delay embedding
    """

    @staticmethod
    def ts_as_supervised(series: pd.Series,
                         n_lags: int,
                         horizon: int,
                         drop_na: bool = True) -> pd.DataFrame:
        """
        Applying time delay embedding to a univariate time series

        Extended description of function.

        Parameters:
        series (pd.Series): A univariate time series
        n_lags (int): Number of past lags
        horizon (int): Size of the forecasting horizon
        drop_na (bool): Whether to drop rows with any missing value

        Returns:
        pd.DataFrame: Reconstructed time series
        """

        n_lags_iter = list(range(n_lags, -horizon, -1))

        X = [series.shift(i) for i in n_lags_iter]
        X = pd.concat(X, axis=1)
        if drop_na:
            X = X.dropna()

        X.columns = [f't-{j - 1}' if j > 0 else f't+{np.abs(j) + 1}'
                     for j in n_lags_iter]
        X.columns = X.columns.str.replace('t-0', 't')

        return X

    @classmethod
    def get_splits(cls,
                   data: Union[pd.Series, Tuple[pd.Series, pd.Series]],
                   n_lags: int,
                   horizon: int,
                   test_size: float,
                   split_vars: bool = True) -> Tuple:

        """
        Getting the train/test splits from a time series

        Train/test split, tde, and splitting X from Y

        Parameters:
        data (pd.Series or Tuple of pd.Series): A univariate time series or the train and test series
        n_lags (int): Number of past lags
        horizon (int): Size of the forecasting horizon
        test_size (float): Ratio of observations to be used as test
        split_vars (bool): Whether to split the predictor variables from the target variables

        Returns:
        Tuple: A set of objects with the reconstructed data
        """

        if isinstance(data, pd.Series):
            train, test = train_test_split(data,
                                           test_size=test_size,
                                           shuffle=SHUFFLE)
        else:
            train, test = data

        train_df = cls.ts_as_supervised(train, horizon=horizon, n_lags=n_lags)
        test_df = cls.ts_as_supervised(test, horizon=horizon, n_lags=n_lags)

        if split_vars:
            is_future = train_df.columns.str.contains('\\+')

            X_train, Y_train = train_df.loc[:, ~is_future], train_df.loc[:, is_future]
            X_test, Y_test = test_df.loc[:, ~is_future], test_df.loc[:, is_future]

            return train, test, X_train, Y_train, X_test, Y_test
        else:
            return train_df, test_df
