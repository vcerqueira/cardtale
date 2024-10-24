import pandas as pd
import statsmodels.stats.api as sms
from statsmodels.formula.api import ols


class Heteroskedasticity:
    TESTS = {
        'white': 'White',
        'breuschpagan': 'Breusch-Pagan',
        'breakvar': 'Goldfeld-Quandt',
    }

    TEST_NAMES = [*TESTS.values()]
    FORMULA = 'value ~ time'

    @classmethod
    def het_tests(cls, series: pd.Series, test: str):
        """
        Testing for heteroskedasticity
        :param series: Univariate time series as pd.Series
        :param test: String denoting the test. One of 'white','goldfeldquandt', or 'breuschpagan'
        :return: p-value as a float.

        If the p-value is high, we accept the null hypothesis that the data is homoskedastic
        """
        assert test in cls.TEST_NAMES, 'Unknown test'

        mod = cls.get_ols_model(series)

        if test == 'White':
            _, p_value, _, _ = sms.het_white(mod.resid, mod.model.exog)
        elif test == 'Goldfeld-Quandt':
            _, p_value, _ = sms.het_goldfeldquandt(mod.resid, mod.model.exog, alternative='two-sided')
        else:
            _, p_value, _, _ = sms.het_breuschpagan(mod.resid, mod.model.exog)

        return p_value

    @classmethod
    def get_ols_residuals(cls, series: pd.Series):
        return cls.get_ols_model(series).resid

    @classmethod
    def get_ols_model(cls, series: pd.Series):
        series = series.reset_index(drop=True).reset_index()
        series.columns = ['time', 'value']
        series['time'] += 1

        olsr = ols(cls.FORMULA, series).fit()

        return olsr

    @classmethod
    def run_all_tests(cls, series: pd.Series):

        test_results = {k: cls.het_tests(series, k) for k in cls.TEST_NAMES}

        return test_results
