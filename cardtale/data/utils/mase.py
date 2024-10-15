import pandas as pd
import numpy as np


class MASE:

    @staticmethod
    def error_1d(y_train: np.ndarray,
                 y_test: np.ndarray,
                 preds: np.ndarray):
        """
        Computes the MEAN-ABSOLUTE SCALED ERROR forcast error for univariate time series prediction.

        See "Another look at measures of forecast accuracy", Rob J Hyndman

        parameters:
            y_train: the series used to train the model, 1d numpy array
            y_test: the test series to predict, 1d numpy array or float
            preds: the prediction of testing_series, 1d numpy array (same size as testing_series) or float
            absolute: "squares" to use sum of squares and root the result, "absolute" to use absolute values.

        """
        n = y_train.shape[0]
        d = np.abs(np.diff(y_train)).sum() / (n - 1)

        errors = np.abs(y_test - preds)

        score = errors.mean() / d

        return score

    @classmethod
    def error_h(cls, preds: pd.DataFrame, y_test: pd.DataFrame, y_train: pd.DataFrame):
        """
        :param preds: predictions by horizon as a pd.DF for a specific model
        :param y_test: testing observations by horizon as a pd.DF
        :param y_train: training observations by horizon as a pd.DF
        :return: mase by horizon
        """

        H = y_test.columns.tolist()

        mase_score = {h: cls.error_1d(preds=preds[h],
                                      y_train=y_train[h],
                                      y_test=y_test[h])
                      for h in H}

        mase_score = pd.Series(mase_score)

        return mase_score
