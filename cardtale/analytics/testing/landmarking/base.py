from typing import Union

import numpy as np
import pandas as pd

from cardtale.data.config.typing import LearningAlgorithm
from cardtale.data.config.landmarks import (HORIZON,
                                     N_LAGS,
                                     TEST_SIZE,
                                     MODEL,
                                     EXPERIMENT_MODES)
from cardtale.data.utils.mase import MASE

UNKNOWN_TEST_ERROR = 'Unknown experiment type'


class Landmarks:

    def __init__(self,
                 test_name: str,
                 model: LearningAlgorithm = MODEL,
                 horizon: int = HORIZON,
                 n_lags: int = N_LAGS,
                 test_size: float = TEST_SIZE):
        assert test_name in [*EXPERIMENT_MODES], UNKNOWN_TEST_ERROR

        self.test_name = test_name
        self.horizon = horizon
        self.n_lags = n_lags
        self.test_size = test_size
        self.model = model

        self.results = {}
        self.importance = {}

    def make_tests(self, series: pd.Series):
        for config in EXPERIMENT_MODES[self.test_name]:
            self.results[config] = self.run_experiment(series, config)

    def run_experiment(self, series: pd.Series, config_name: str):
        pass

    def train_and_predict(self,
                          X_train: pd.DataFrame,
                          Y_train: Union[pd.DataFrame, pd.Series],
                          X_test: pd.DataFrame):
        self.model.fit(X_train, Y_train)
        predictions = self.model.predict(X_test)

        predictions_df = pd.DataFrame(predictions, columns=Y_train.columns)
        predictions_df.index = X_test.index

        return predictions_df

    @staticmethod
    def score(y_test: Union[pd.DataFrame, np.ndarray],
              preds: Union[pd.DataFrame, np.ndarray],
              y_train: Union[pd.DataFrame, np.ndarray]):

        if isinstance(y_test, pd.DataFrame):
            error_by_h = MASE.error_h(preds=preds, y_test=y_test, y_train=y_train)
            error = error_by_h.mean()
        else:
            error = MASE.error_1d(preds=preds, y_test=y_test, y_train=y_train)
            error_by_h = {}

        return error_by_h, error
