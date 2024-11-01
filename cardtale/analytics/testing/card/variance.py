from typing import Dict, Tuple

import pandas as pd

from cardtale.analytics.operations.landmarking.variance import VarianceLandmarks
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.analytics.operations.tsa.log import LogTransformation
from cardtale.analytics.operations.tsa.distributions import KolmogorovSmirnov
from cardtale.analytics.operations.tsa.heteroskedasticity import Heteroskedasticity
from cardtale.core.config.analysis import ALPHA
from cardtale.core.data import TimeSeriesData


class VarianceTesting(UnivariateTester):
    """
    Class for analyzing variance in a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        prob_heteroskedastic (float): Probability of heteroskedasticity.
        groups_with_diff_var (list): List of groups with different variance.
        residuals (pd.Series): Residuals from OLS regression.
        distr_original (str): Original distribution.
        distr_logt (str): Distribution after logarithm transformation.
    """

    def __init__(self, tsd: TimeSeriesData):
        """
        Initializes the VarianceTesting with the given time series data.

        Args:
            tsd (TimeSeriesData): Time series data object.
        """

        super().__init__(tsd)

        self.prob_heteroskedastic: float = -1
        self.groups_with_diff_var = []
        self.residuals = None

        self.distr_original = None
        self.distr_logt = None

    def run_statistical_tests(self):
        self.tests = Heteroskedasticity.run_all_tests(self.series)
        self.residuals = Heteroskedasticity.get_ols_residuals(self.series)

        self.tests = pd.Series(self.tests)
        self.tests = (self.tests < ALPHA).astype(int)

        self.prob_heteroskedastic = self.tests.mean()

        series_t = LogTransformation.transform(self.series)

        self.distr_original, self.distr_logt = \
            KolmogorovSmirnov.best_dist_in_two_parts(self.series, series_t)

    def run_landmarks(self):
        var_lm = VarianceLandmarks(tsd=self.tsd)
        var_lm.run()

        self.performance = var_lm.results

    def run_misc(self):
        """
        Runs miscellaneous experiments for variance.
        """
        pass


class VarianceTestsParser:
    """
    Class for parsing variance test results and generating analysis text.

    Methods:
        show_distribution_plot(tests: VarianceTesting) -> Tuple[bool, Dict]:
            Determines which distribution plots to show based on variance test results.
    """

    @staticmethod
    def show_distribution_plot(tests: VarianceTesting) -> Tuple[bool, Dict]:
        """
        Determines which distribution plots to show based on variance test results.

        Args:
            tests (VarianceTesting): Object containing the variance test results.

        Returns:
            Tuple[bool, Dict]: Flag indicating whether to show the distribution plots and dictionary of results.
        """
        is_heteroskedastic = tests.prob_heteroskedastic > 0
        log_improves = tests.performance['base'] > tests.performance['log']
        boxcox_improves = tests.performance['base'] > tests.performance['boxcox']
        exists_groupdiff = len(tests.groups_with_diff_var) > 0

        show_results = {
            'by_st': is_heteroskedastic,
            'by_log': log_improves,
            'by_boxcox': boxcox_improves,
            'by_groupdiff': exists_groupdiff,
        }

        show_me = any([*show_results.values()])

        return show_me, show_results
