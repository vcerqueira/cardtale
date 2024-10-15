import pandas as pd

from cardtale.analytics.testing.components.trend import TrendTesting
from cardtale.analytics.testing.components.seasonality import SeasonalityTestingMulti
from cardtale.analytics.testing.components.variance import VarianceTesting
from cardtale.analytics.testing.components.change import ChangeTesting
from cardtale.data.config.typing import Period

INDEX_NOT_DTI_ERROR = 'Time series index must be a pd.DatetimeIndex object'


class TestingMetaData:

    def __init__(self,
                 series: pd.Series,
                 frequency_df: pd.DataFrame,
                 period: Period):
        self.series = series
        self.n = self.series.__len__()
        self.frequency_df = frequency_df
        self.period = period


class TestingComponents:
    """
    This is an class which combines all the tests and experiments

    Attributes:
        metadata (TestingMetaData): Time series metadata
        trend (TrendTesting): Trend tests
        variance (VarianceTesting): Variance tests
        change (ChangeTesting): Change tests
        seasonality (SeasonalityTestingMulti): Seasonality tests
    """

    def __init__(self,
                 series: pd.Series,
                 frequency_df: pd.DataFrame,
                 period: Period):
        assert isinstance(series.index, pd.DatetimeIndex), INDEX_NOT_DTI_ERROR

        self.metadata = TestingMetaData(
            series=series,
            frequency_df=frequency_df,
            period=period
        )

        self.trend = TrendTesting(series)
        self.variance = VarianceTesting(series)
        self.change = ChangeTesting(series)
        self.seasonality = SeasonalityTestingMulti(series,
                                                   self.metadata.frequency_df,
                                                   self.metadata.period)

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


