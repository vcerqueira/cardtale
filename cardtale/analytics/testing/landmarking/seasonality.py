from typing import Optional

import pandas as pd

from cardtale.analytics.tsa.fourier import FourierTerms
from cardtale.analytics.tsa.rbf import RBFTerms
from cardtale.analytics.tsa.tde import TimeDelayEmbedding
from cardtale.analytics.testing.landmarking.base import Landmarks
from cardtale.data.config.landmarks import EXPERIMENT_MODES, N_TERMS
from cardtale.data.config.typing import Period

TEST_NAME = 'seasonality'


class SeasonalLandmarks(Landmarks):

    def __init__(self, period: Period):

        super().__init__(test_name=TEST_NAME)

        self.period = period

    def run_experiment(self,
                       series: pd.Series,
                       config_name: str):
        """
        todo get importance of seasonal features
        """

        config = EXPERIMENT_MODES[self.test_name][config_name]

        _, _, X_train, Y_train, X_test, Y_test = \
            TimeDelayEmbedding.get_splits(data=series,
                                          horizon=self.horizon,
                                          n_lags=self.n_lags,
                                          test_size=self.test_size)

        train_x = [X_train]
        test_x = [X_test]

        if config['fourier']:
            if self.period is not None:
                fourier = FourierTerms(n_terms=N_TERMS,
                                       period=self.period,
                                       prefix=f'Period={self.period}_')
                train_x.append(fourier.transform(X_train.index))
                test_x.append(fourier.transform(X_test.index))

        train_x_df = pd.concat(train_x, axis=1)
        test_x_df = pd.concat(test_x, axis=1)

        preds = self.train_and_predict(train_x_df, Y_train, test_x_df)

        error_by_h, error = self.score(Y_test, preds, Y_train)

        return error
