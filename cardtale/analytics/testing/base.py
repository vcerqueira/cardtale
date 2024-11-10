from cardtale.analytics.testing.card.trend import UnivariateTrendTesting
from cardtale.analytics.testing.card.seasonality import SeasonalityTestingMulti
from cardtale.analytics.testing.card.variance import VarianceTesting
from cardtale.analytics.testing.card.change import ChangeTesting
from cardtale.core.data import TimeSeriesData


class TestingComponents:
    """
    This is a class which combines all the tests and experiments.

    Attributes:
        trend (TrendTesting): Trend tests.
        variance (VarianceTesting): Variance tests.
        change (ChangeTesting): Change tests.
        seasonality (SeasonalityTestingMulti): Seasonality tests.
    """

    def __init__(self, tsd: TimeSeriesData):
        """
        Initializes the TestingComponents with the given time series data.

        Args:
            tsd (TimeSeriesData): Time series data object.
        """

        self.trend = UnivariateTrendTesting(tsd)
        self.variance = VarianceTesting(tsd)
        self.change = ChangeTesting(tsd)
        self.seasonality = SeasonalityTestingMulti(tsd=tsd)

    def run(self):
        """
        Run all tests
        """
        print('Tests: Trend')
        self.trend.run_statistical_tests()
        self.trend.run_landmarks()
        self.trend.run_misc()

        print('Tests: Seasonality')
        self.seasonality.run_tests()
        self.seasonality.run_misc()

        print('Tests: Variance')
        print('\trun_statistical_tests')
        self.variance.run_statistical_tests()
        print('\trun_landmarks')
        self.variance.run_landmarks()
        print('\trun_misc')
        self.variance.run_misc()

        print('Tests: Change Points')
        self.change.run_misc()
        self.change.run_statistical_tests()
        self.change.run_landmarks()
