import pandas as pd

from cardtale.analytics.testing.components.trend import UnivariateTrendTesting
from cardtale.analytics.testing.components.seasonality import SeasonalityTestingMulti
from cardtale.analytics.testing.components.variance import VarianceTesting
from cardtale.analytics.testing.components.change import ChangeTesting
from cardtale.core.config.typing import Period
from cardtale.core.data import TimeSeriesData

#
# class TestingMetaData:
#
#     def __init__(self,
#                  df: pd.DataFrame,
#                  time_col: str,
#                  target_col: str,
#                  freq_df: pd.DataFrame,
#                  period: Period):
#         """
#         todo docs
#
#         :param df: Time series dataset
#         :type df: pd.DataFrame
#
#         :param time_col:
#         :param target_col:
#
#         :param freq_df:
#
#         :param period:
#         """
#         self.df = df
#         self.time_col = time_col
#         self.target_col = target_col
#         self.n = self.df.shape[0]
#         self.freq_df = freq_df
#         self.period = period
#

class TestingComponents:
    """
    todo docs
    This is an class which combines all the tests and experiments

    Attributes:
        metadata (TestingMetaData): Time series metadata
        trend (TrendTesting): Trend tests
        variance (VarianceTesting): Variance tests
        change (ChangeTesting): Change tests
        seasonality (SeasonalityTestingMulti): Seasonality tests
    """

    def __init__(self, tsd: TimeSeriesData):

        self.trend = UnivariateTrendTesting(tsd)
        self.variance = VarianceTesting(tsd)
        self.change = ChangeTesting(tsd)
        self.seasonality = SeasonalityTestingMulti(tsd=tsd)

    def run(self, seasonal_df: pd.DataFrame):
        """
        Run all tests

        :param seasonal_df: Seasonal data
        """
        self.trend.run_statistical_tests()
        self.trend.run_landmarks()
        self.trend.run_misc()

        self.seasonality.run_tests(seasonal_df)

        self.variance.run_statistical_tests()
        self.variance.run_landmarks()
        self.variance.run_misc()
        self.variance.group_var = self.seasonality.group_var

        self.change.run_statistical_tests()
        self.change.run_landmarks()
        self.change.run_misc()
