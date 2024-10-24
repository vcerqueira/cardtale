from cardtale.analytics.testing.card.trend import UnivariateTrendTesting
from cardtale.analytics.testing.card.seasonality import SeasonalityTestingMulti
from cardtale.analytics.testing.card.variance import VarianceTesting
from cardtale.analytics.testing.card.change import ChangeTesting
from cardtale.core.data import TimeSeriesData


class TestingComponents:
    """
    This is an class which combines all the tests and experiments

    Attributes:
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

    def run(self):
        """
        Run all tests

        """
        self.trend.run_statistical_tests()
        self.trend.run_landmarks()
        self.trend.run_misc()

        self.seasonality.run_tests()

        self.variance.run_statistical_tests()
        self.variance.run_landmarks()
        self.variance.run_misc()
        self.variance.group_var = self.seasonality.group_var

        self.change.run_statistical_tests()
        self.change.run_landmarks()
        self.change.run_misc()
