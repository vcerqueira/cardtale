import pandas as pd
import statsmodels.stats.api as sms
from statsmodels.formula.api import ols
from statsmodels.tsa.stattools import breakvar_heteroskedasticity_test

from patsy import dmatrices

HETEROSKEDASTICITY_TESTS = {
    'white': 'White',
    'breuschpagan': 'Breusch-Pagan',
    'breakvar': 'Goldfeld-Quandt',
}


def het_tests(series: pd.Series,
              test: str,
              return_residuals: bool = False) -> float:
    """
    Testing for heteroskedasticity using the White or Breusch-Pagan test.
    If the p-value is high, we accept the null hypothesis that there is no heteroscedastisticity

    :param return_residuals:
    :param series: Univariate time series as pd.Series
    :param test: String denoting the test. One of 'white' or 'breuschpagan'

    :return: p-value as a float.
    """
    formula = 'value ~ time'
    assert test in [*HETEROSKEDASTICITY_TESTS], 'Unknown test'

    series = series.reset_index(drop=True).reset_index()
    series.columns = ['time', 'value']
    series['time'] += 1

    olsr = ols(formula, series).fit()

    y, X = dmatrices(formula, series, return_type='dataframe')

    if test == 'white':
        _, p_value, _, _ = sms.het_white(olsr.resid, X)
    elif test == 'breakvar':
        _, p_value = breakvar_heteroskedasticity_test(olsr.resid)
    else:
        _, p_value, _, _ = sms.het_breuschpagan(olsr.resid, X)

    if return_residuals:
        return p_value, olsr.resid

    return p_value
