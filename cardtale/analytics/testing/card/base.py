from cardtale.core.data import TimeSeriesData


class Tester:
    """
    Tester abstract class

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        tests (dict): Test results.
        performance (dict): Performance results.
    """

    def __init__(self, tsd: TimeSeriesData):
        self.tsd = tsd
        self.tests = {}
        self.performance = {}

    def run_statistical_tests(self):
        """
        Running statistical tests
        """
        raise NotImplementedError

    def run_landmarks(self):
        """
        Running landmark experiments
        """
        raise NotImplementedError

    def run_misc(self, **kwargs):
        """
        Running miscellaneous experiments
        """
        raise NotImplementedError


class UnivariateTester(Tester):
    """
    UnivariateTester class for running univariate tests on time series data.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        series (pd.Series): Target series extracted from the time series data.
    """

    def __init__(self, tsd: TimeSeriesData):
        """
        Initializes the UnivariateTester with the given time series data.

        Args:
            tsd (TimeSeriesData): Time series data object.
        """

        super().__init__(tsd)

        self.series = tsd.get_target_series(df=self.tsd.df,
                                            time_col=self.tsd.time_col,
                                            target_col=self.tsd.target_col)

    def run_statistical_tests(self):
        pass

    def run_landmarks(self):
        pass

    def run_misc(self, **kwargs):
        pass
