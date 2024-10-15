import pandas as pd


class Tester:
    """
    Tester abstract class

    Attributes:
        series (pd.Series): Univariate time series
        tests (dict): Test results
        performance (dict): Performance results
    """

    def __init__(self, series: pd.Series):
        self.series = series
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
