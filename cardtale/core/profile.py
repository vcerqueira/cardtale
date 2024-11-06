import warnings

from typing import List

import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis, kurtosistest, skewtest

from cardtale.analytics.operations.tsa.distributions import KolmogorovSmirnov
from cardtale.analytics.operations.tsa.acf import AutoCorrelation
from cardtale.core.config.analysis import ALPHA, STATS_TO_ROUND, ROUND_N
from cardtale.analytics.operations.tsa.log import LogTransformation

warnings.filterwarnings('ignore', category=RuntimeWarning)


class SeriesProfile:
    """
    This is a class for summarising the time series (descriptive stats)

    Attributes:
        n (int): Number of data points
        alpha (float): Significance level
        dt_range (List): Sampling period
        stats (pd.Series): Basic stats, incl. 3rd/4th moments
        kurtosis_like_normal (bool): If should reject the hypothesis
        that kurtosis is that of a Normal
        skewness_like_normal (bool): If should reject the hypothesis
        that skewness is that of a Normal
        n_outliers_upper (int): Number of upper outliers
        n_outliers_lower (int): Number of lower outliers
        n_outliers (int): Number of outliers
        perc_outliers (float): % of outliers
        perc_upp_outliers (float): % of upper outliers
        reject_dists (list): Rejected distributions
        reject_dist_nms (list): Named rejected distributions
        n_reject_dists (list): Acceptable distributions
        n_reject_dist_nms (list): Named Acceptable distributions
        acf (AutoCorrelation): Auto-correlation class object
    """

    def __init__(self, n_lags: int, alpha: float = ALPHA):
        """
        Class constructor.

        Args:
            n_lags (int): Number of lags for auto-correlation.
            alpha (float): Significance level.
        """

        self.n = -1
        self.alpha = alpha

        self.dt_range: List = []
        self.stats: pd.Series = pd.Series(dtype=float)

        self.kurtosis_like_normal: bool = False
        self.skewness_like_normal: bool = False

        self.n_outliers_upper: int = -1
        self.n_outliers_lower: int = -1
        self.n_outliers: int = -1
        self.perc_outliers: float = -1.
        self.perc_upp_outliers: float = -1.

        self.reject_dists = []
        self.reject_dist_nms = []
        self.n_reject_dists = []
        self.n_reject_dist_nms = []

        self.acf = AutoCorrelation(n_lags=n_lags, alpha=ALPHA)
        self.pacf = AutoCorrelation(n_lags=n_lags, alpha=ALPHA)

        self.ns_zones = None

        self.growth = {}

    def run(self, series: pd.Series, period: int, dt_format: str, ):
        """
        Runs the summary and distribution fitting for the series.

        Args:
            series (pd.Series): A univariate time series.
            period (int): Time series seasonal period.
            dt_format (str): Date format for display.
        """

        self.summarise(series, period, dt_format)
        self.growth_analysis(series)

    def summarise(self, series: pd.Series, period: int, dt_format: str):
        """
        Summarises a time series.

        Args:
            series (pd.Series): A univariate time series.
            period (int): Time series seasonal period.
            dt_format (str): Date format for display.

        Returns:
            self: Summarised time series.
        """

        self.n = len(series)
        self.dt_range = series.index[[0, -1]]
        self.dt_range = [x.strftime(dt_format) for x in self.dt_range]

        self.stats = series.describe()
        self.stats['skew'] = skew(series.values)
        self.stats['kurtosis'] = kurtosis(series)
        self.stats['first_value'] = series.values[0]
        self.stats['last_value'] = series.values[-1]
        self.stats['nan_percentage'] = np.round(100 * series.isna().sum() / self.n, 2)

        pct_c = series.pct_change()

        self.stats['growth_average'] = np.round(pct_c.mean() * 100, 2)
        self.stats['growth_median'] = np.round(pct_c.median() * 100, 2)

        self.kurtosis_like_normal = kurtosistest(series).pvalue < self.alpha
        self.skewness_like_normal = skewtest(series).pvalue < self.alpha

        self.stats['iqr'] = self.stats['75%'] - self.stats['25%']

        # todo this outlier analysis is obsolete, rigth?
        upper_outliers = series > self.stats['75%'] + self.stats['iqr'] * 1.5
        lower_outliers = series < self.stats['25%'] - self.stats['iqr'] * 1.5
        self.n_outliers_upper = np.sum(upper_outliers)
        self.n_outliers_lower = np.sum(lower_outliers)
        self.n_outliers = self.n_outliers_upper + self.n_outliers_lower
        self.perc_outliers = np.round(100 * (self.n_outliers / self.stats['count']), 2)
        self.perc_upp_outliers = np.round(100 * (self.n_outliers_upper / self.n_outliers), 2)

        self.acf.calc_acf(series)
        self.acf.significance_analysis(period=period)
        self.pacf.calc_pacf(series)
        self.pacf.significance_analysis(period=period)

        # self.ns_zones = NasonPeriods.get_segments_df(series)

        self.stats = self.stats.to_dict()
        for st, val in self.stats.items():
            if np.isinf(val):
                continue

            self.stats[st] = int(val) if val == int(val) else val

            if st in STATS_TO_ROUND:
                self.stats[st] = np.round(self.stats[st], ROUND_N)

    def growth_analysis(self, series: pd.Series):

        rets = LogTransformation.returns(series)[1:]

        mean_rets = rets.mean()
        std_rets = rets.std()

        # Calculate bounds
        upper_bound = mean_rets + 2 * std_rets
        lower_bound = mean_rets - 2 * std_rets

        # Calculate percentage of extreme values
        extreme_pct = ((rets > upper_bound) | (rets < lower_bound)).mean() * 100

        # Growth Stability/Patterns:
        self.growth = {
            'upward_moves_mag': rets[rets > 0].mean(),
            'upward_moves_prob': (rets > 0).mean() * 100,
            'downward_moves_mag': rets[rets < 0].mean(),
            'downward_moves_prob': (rets < 0).mean() * 100,
            # Growth Direction Changes
            'direction_changes': (rets > 0).diff().abs().sum(),

            # dist
            'average_ret': mean_rets,
            'median_ret': rets.median(),
            'growth_volatility': std_rets,
            'kurtosis': kurtosis(rets),
            'kurtosis_like_normal': kurtosistest(rets).pvalue > ALPHA,
            'skewness': skew(rets),
            'skewness_like_normal': skewtest(rets).pvalue > ALPHA,

            # Extreme Movements
            'extreme_pct': extreme_pct,
            'largest_increase': rets.max(),
            'largest_increase_loc': rets.argmax(),
            'largest_decrease': rets.min(),
            'largest_decrease_loc': rets.argmin(),
        }
