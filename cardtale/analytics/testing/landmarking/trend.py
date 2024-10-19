import pandas as pd

from cardtale.analytics.tsa.tde import TimeDelayEmbedding
from cardtale.analytics.testing.preprocess.differencing import Differencing
from cardtale.analytics.testing.landmarking.base import Landmarks
from cardtale.core.config.landmarks import EXPERIMENT_MODES

TEST_NAME = 'trend'

pd.options.mode.chained_assignment = None


class TrendLandmarks(Landmarks):

    def __init__(self):
        super().__init__(test_name=TEST_NAME)

    def run_experiment(self, series: pd.Series, config_name: str):


        config = EXPERIMENT_MODES[self.test_name][config_name]

        if config['n_diffs'] == 1:

            train_df, test_df = \
                TimeDelayEmbedding.get_splits(data=series,
                                              horizon=self.horizon,
                                              n_lags=self.n_lags + 1,
                                              test_size=self.test_size,
                                              split_vars=False)

            test_df_or = test_df.copy()

            train_df = train_df.diff(axis=1)
            train_df = train_df.iloc[:, 1:]
            test_df = test_df.diff(axis=1)
            test_df = test_df.iloc[:, 1:]

            is_future = train_df.columns.str.contains('\\+')
            X_train, Y_train = train_df.loc[:, ~is_future], train_df.loc[:, is_future]
            X_test, Y_test = test_df.loc[:, ~is_future], test_df.loc[:, is_future]
            X_test_or = test_df_or.loc[:, ~test_df_or.columns.str.contains('\\+')]
            Y_test_or = test_df_or.loc[:, test_df_or.columns.str.contains('\\+')]
        else:
            _, _, X_train, Y_train, X_test, Y_test = \
                TimeDelayEmbedding.get_splits(data=series,
                                              horizon=self.horizon,
                                              n_lags=self.n_lags,
                                              test_size=self.test_size)

            X_test_or, Y_test_or = X_test.copy(), Y_test.copy()

        if config['T']:
            X_train['time'] = range(X_train.shape[0])
            X_test['time'] = range(X_train.shape[0], X_train.shape[0] + X_test.shape[0])

        preds = self.train_and_predict(X_train, Y_train, X_test)

        if config['n_diffs'] == 1:
            preds = Differencing.diff_inv_df(preds, X_test_or['t'].values)

        error_by_h, error = self.score(Y_test_or, preds, Y_train)

        return error
