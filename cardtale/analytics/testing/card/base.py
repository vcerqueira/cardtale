from cardtale.core.data import TimeSeriesData


class Tester:
    """
    Tester abstract class

    todo docs

    Attributes:
        tests (dict): Test results
        performance (dict): Performance results
    """

    def __init__(self, tsd: TimeSeriesData):
        self.tsd = tsd
        self.tests = {}
        self.performance = {}

    def run_statistical_tests(self):
        """
        Running statistical tests
        """
        pass

    def run_landmarks(self):
        """
        Running landmark experiments
        """
        pass

    def run_misc(self, **kwargs):
        """
        Running miscellaneous experiments
        """
        pass


class UnivariateTester(Tester):

    def __init__(self, tsd: TimeSeriesData):
        super().__init__(tsd)

        self.series = tsd.get_target_series(df=self.tsd.df,
                                            time_col=self.tsd.time_col,
                                            target_col=self.tsd.target_col)
