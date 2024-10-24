# https://alkaline-ml.com/pmdarima/modules/generated/pmdarima.arima.OCSBTest.html
# https://medium.com/towards-data-science/understanding-time-series-trend-addfd9d7764e

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import kpss, adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy import stats
import warnings

# https://arch.readthedocs.io/en/latest/unitroot/unitroot_examples.html#Phillips-Perron-Testing
# https://geobosh.github.io/uroot/reference/index.html

class DifferencingTests:
    """Seasonal and non-seasonal differencing tests

    """

    NSDIFF_TESTS = {
        'seas': 'Wang-Smith-Hyndman',
        'ocsb': 'OCSB',
        'hegy': 'HEGY',
        'ch': 'Canova-Hansen'
    }

    NDIFF_TESTS = {
        'kpss': 'KPSS',
        'adf': 'Augmented Dickey-Fuller',
        'pp': 'PP'
    }

    TEST_TYPES = ['trend', 'level']

    @staticmethod
    def nsdiffs(series: pd.Series, frequency: int, test: str = 'seas') -> int:
        """
        Estimate number of seasonal differences required for seasonal stationarity.

        Parameters:
        -----------
        series : pd.Series
            Time series data
        frequency : int
            Seasonal period
        test : str
            Type of test to use ('seas', 'ocsb', 'hegy', or 'ch')

        Returns:
        --------
        int : Recommended number of seasonal differences
        """
        if test not in TimeDifferencingTests.NSDIFF_TESTS:
            raise ValueError(f"Unknown test type. Must be one of {list(TimeDifferencingTests.NSDIFF_TESTS.keys())}")

        if len(series) < 2 * frequency:
            warnings.warn("Series too short for seasonal differencing test")
            return 0

        if test == 'seas':
            return TimeDifferencingTests._wang_smith_hyndman_test(series, frequency)
        elif test == 'ocsb':
            return TimeDifferencingTests._ocsb_test(series, frequency)
        elif test == 'ch':
            return TimeDifferencingTests._canova_hansen_test(series, frequency)
        else:  # hegy
            return TimeDifferencingTests._hegy_test(series, frequency)

    @staticmethod
    def ndiffs(series: pd.Series, test: str = 'kpss', test_type: str = 'trend') -> int:
        """
        Estimate number of differences required for non-seasonal stationarity.

        Parameters:
        -----------
        series : pd.Series
            Time series data
        test : str
            Type of test to use ('kpss', 'adf', or 'pp')
        test_type : str
            Type of test ('trend' or 'level')

        Returns:
        --------
        int : Recommended number of differences
        """
        if test not in TimeDifferencingTests.NDIFF_TESTS:
            raise ValueError(f"Unknown test type. Must be one of {list(TimeDifferencingTests.NDIFF_TESTS.keys())}")

        if test_type not in TimeDifferencingTests.TEST_TYPES:
            raise ValueError(f"Unknown test_type. Must be one of {TimeDifferencingTests.TEST_TYPES}")

        max_d = min(2, int(len(series) / 3))  # Maximum number of differences
        d = 0

        while d <= max_d:
            is_stationary = TimeDifferencingTests._check_stationarity(series, test, test_type)
            if is_stationary:
                return d
            series = series.diff().dropna()
            d += 1

        return d

    @staticmethod
    def _check_stationarity(series: pd.Series, test: str, test_type: str) -> bool:
        """Check if series is stationary using specified test"""
        if test == 'kpss':
            regression = 'ct' if test_type == 'trend' else 'c'
            stat, p_value, *_ = kpss(series, regression=regression)
            return p_value > 0.05

        elif test == 'adf':
            regression = 'ct' if test_type == 'trend' else 'c'
            stat, p_value, *_ = adfuller(series, regression=regression)
            return p_value < 0.05

        else:  # pp test
            # Note: Pure Python Phillips-Perron test implementation would be quite complex
            # Using ADF as fallback, but you might want to use statsmodels PP test when available
            regression = 'ct' if test_type == 'trend' else 'c'
            stat, p_value, *_ = adfuller(series, regression=regression)
            return p_value < 0.05

    @staticmethod
    def _wang_smith_hyndman_test(series: pd.Series, frequency: int) -> int:
        """Implementation of Wang-Smith-Hyndman seasonal strength test"""
        decomposition = seasonal_decompose(series, period=frequency, extrapolate_trend='freq')
        seasonal = decomposition.seasonal
        resid = decomposition.resid

        # Calculate variance of seasonal and residual components
        var_seasonal = np.var(seasonal)
        var_resid = np.var(resid)

        # Calculate seasonal strength
        seasonal_strength = max(0, min(1, var_seasonal / (var_seasonal + var_resid)))

        # If seasonal strength is greater than 0.64, suggest seasonal differencing
        return 1 if seasonal_strength > 0.64 else 0

    @staticmethod
    def _ocsb_test(series: pd.Series, frequency: int) -> int:
        """
        Simplified OCSB test
        """
        # seasonal differences
        seasonal_diff = series.diff(frequency).dropna()

        # Perform ADF test on seasonal differences
        _, p_value, *_ = adfuller(seasonal_diff)

        # If p-value < 0.05, series needs seasonal differencing
        return 1 if p_value < 0.05 else 0

    @staticmethod
    def _canova_hansen_test(series: pd.Series, frequency: int) -> int:
        """
        Simplified Canova-Hansen test

        """
        # de-trend
        detrended = series - pd.Series(np.polynomial.polynomial.polyfit(
            np.arange(len(series)), series, deg=1)).values

        # seasonal dummy variables
        seasonal_dummies = pd.get_dummies(np.arange(len(series)) % frequency)

        # Calculate test statistic
        test_stat = np.sum(np.square(
            seasonal_dummies.T.dot(detrended))) / (len(series) * frequency)

        # Critical value (approximate)
        critical_value = 0.461  # 5% significance level

        n_diffs = 1 if test_stat > critical_value else 0

        return n_diffs

    @staticmethod
    def _hegy_test(series: pd.Series, frequency: int) -> int:
        """
        Simplified HEGY test
        """

        seasonal_diff = series.diff(frequency).dropna()

        # seasonal unit roots
        _, p_value, *_ = adfuller(seasonal_diff)

        n_diffs = 1 if p_value < 0.05 else 0

        return n_diffs
