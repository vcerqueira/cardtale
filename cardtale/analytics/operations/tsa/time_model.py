import pandas as pd
from scipy.stats import linregress

from cardtale.core.config.analysis import CORRELATION_TESTS


class TimeLinearModel:
    """
    This is a class for quantifying the effect of time on the time series

    Attributes:
        model (linregress): Linear model from scipy.stats
        time_corr (dict): Correlation between time series and time for several correlation functions
        time_corr_avg (float): Average correlation between time series and time
        side (str): Textual description of whether the correlation is negative or positive
    """

    def __init__(self):
        self.model = None
        self.time_corr = -1
        self.time_corr_avg = -1
        self.side = ''

    def fit(self, series: pd.Series):
        """
        Quantifying how the time variable explains the series.
        todo include tedd tests

        Args:
            series (pd.Series): A univariate time series.

        Returns:
            self: Fitted class object.
        """

        aux_df = pd.DataFrame({'Series': series,
                               'Time': range(len(series))})

        aux_df['Time'] += 1

        self.model = linregress(aux_df['Series'], aux_df['Time'])

        self.time_corr = {k: aux_df.corr(method=k)['Series']['Time']
                          for k in CORRELATION_TESTS}

        self.time_corr_avg = pd.Series(self.time_corr).mean()
        if self.time_corr_avg > 0:
            self.side = 'upward'
        else:
            self.side = 'downward'
