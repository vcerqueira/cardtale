from typing import Optional

import pandas as pd

from cardtale.analytics.tsa.tde import TimeDelayEmbedding
from cardtale.analytics.testing.landmarking.base import Landmarks
from cardtale.analytics.testing.preprocess.log import LogTransformation
from cardtale.analytics.testing.preprocess.boxcox import BoxCox
from cardtale.data.config.landmarks import EXPERIMENT_MODES

TEST_NAME = 'variance'


class VarianceLandmarks(Landmarks):

    def __init__(self):
        super().__init__(test_name=TEST_NAME)

        self.box_cox: Optional[BoxCox] = None

    def run_experiment(self, series: pd.Series, config_name: str):

        config = EXPERIMENT_MODES[self.test_name][config_name]

        train, test, X_train, Y_train, X_test, Y_test = \
            TimeDelayEmbedding.get_splits(data=series,
                                          horizon=self.horizon,
                                          n_lags=self.n_lags,
                                          test_size=self.test_size)

        Y_test_or = Y_test.copy()
        Y_train_or = Y_train.copy()

        if config['log']:
            X_train = LogTransformation.transform(X_train)
            Y_train = LogTransformation.transform(Y_train)
            X_test = LogTransformation.transform(X_test)
        elif config['boxcox']:
            self.box_cox = BoxCox()
            _ = self.box_cox.transform(train)

            X_train = self.box_cox.transform_df_lambda(X_train)
            Y_train = self.box_cox.transform_df_lambda(Y_train)
            X_test = self.box_cox.transform_df_lambda(X_test)

        preds = self.train_and_predict(X_train, Y_train, X_test)

        if config['log']:
            preds = LogTransformation.inverse_transform(preds)
        elif config['boxcox']:
            preds = self.box_cox.inverse_transform_df(preds)

        preds.index = Y_test_or.index

        error_by_h, error = self.score(Y_test_or, preds, Y_train_or)

        return error
