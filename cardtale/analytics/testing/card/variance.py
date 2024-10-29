import pandas as pd

from cardtale.analytics.operations.landmarking.variance import VarianceLandmarks
from cardtale.analytics.testing.card.base import UnivariateTester
from cardtale.analytics.operations.tsa.log import LogTransformation
from cardtale.analytics.operations.tsa.distributions import KolmogorovSmirnov
from cardtale.analytics.operations.tsa.heteroskedasticity import Heteroskedasticity
from cardtale.core.config.analysis import ALPHA
from cardtale.core.data import TimeSeriesData


class VarianceTesting(UnivariateTester):

    def __init__(self, tsd: TimeSeriesData):
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
