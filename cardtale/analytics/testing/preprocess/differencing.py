import numpy as np
import pandas as pd


class Differencing:

    @staticmethod
    def diff_inv_vector(x_diff: np.ndarray, x0):
        return np.r_[x0, x_diff].cumsum()[1:]

    @classmethod
    def diff_inv_df(cls, data: pd.DataFrame, previous_values: np.ndarray):
        """
        invert differencing on a predictions dataframe
        :param data: differenced predictions
        :param previous_values
        """
        diff_inv_l = []
        for i, x in enumerate(data.values):
            di_x = cls.diff_inv_vector(data.values[i], previous_values[i])
            diff_inv_l.append(di_x)

        predictions_df = pd.DataFrame(diff_inv_l, columns=data.columns)
        predictions_df.index = data.index

        return predictions_df
