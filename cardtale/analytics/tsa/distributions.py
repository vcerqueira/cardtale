import warnings

from scipy.stats.stats import kstest
from scipy import stats

import pandas as pd

from cardtale.core.config.analysis import ALPHA

warnings.filterwarnings('ignore', category=RuntimeWarning)

C_DISTRIBUTIONS = {
    'cauchy': 'Cauchy',
    'chi': 'Chi-squared',
    'expon': 'Exponential',
    'exponnorm': 'Exponentially Modified Gaussian distribution',
    'gamma': 'Gamma',
    'logistic': 'Logistic',
    'lognorm': 'Log-Normal',
    'norm': 'Gaussian',
    'pareto': 'Pareto',
    'powerlaw': 'Power-law',
}


class KolmogorovSmirnov:

    @staticmethod
    def test_distributions(series: pd.Series):
        p_values = {}
        for dist_name in C_DISTRIBUTIONS:
            dist = getattr(stats, dist_name)
            param = dist.fit(series)

            # Applying the Kolmogorov-Smirnov test
            D, dist_p_value = kstest(series, dist_name, args=param)

            p_values[C_DISTRIBUTIONS[dist_name]] = dist_p_value

        p_values = pd.Series(p_values)
        p_values = p_values.sort_values(ascending=False)

        rejected = p_values[p_values < ALPHA].index.tolist()
        not_rejected = p_values[p_values > ALPHA]

        return rejected, not_rejected

    @classmethod
    def best_dist_in_two_parts(cls, series1: pd.Series, series2: pd.Series):

        _, dist1 = cls.test_distributions(series1)
        _, dist2 = cls.test_distributions(series2)

        if len(dist1) > 0:
            best_dist_p1 = dist1.index[0]
        else:
            best_dist_p1 = None

        if len(dist2) > 0:
            best_dist_p2 = dist2.index[0]
        else:
            best_dist_p2 = None

        return best_dist_p1, best_dist_p2
