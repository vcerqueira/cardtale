import pandas as pd

import rpy2.robjects as r_objects
from rpy2.robjects import pandas2ri

R_NSDIFF_TESTS = {
    'seas': 'Wang-Smith-Hyndman',
    'ocsb': 'OCSB',
    'hegy': 'HEGY',
    'ch': 'Canova-Hansen'
}

# https://alkaline-ml.com/pmdarima/modules/generated/pmdarima.arima.OCSBTest.html

# https://medium.com/towards-data-science/understanding-time-series-trend-addfd9d7764e

R_NDIFF_TESTS = {
    'kpss': 'KPSS',
    'adf': 'Augmented Dickey-Fuller',
    'pp': 'PP',
}

TEST_TYPES = ['trend', 'level']


class RNDiffs:

    @staticmethod
    def r_nsdiffs(series: pd.Series,
                  frequency: int,
                  test: str):
        pandas2ri.activate()

        series_rpy = pandas2ri.py2rpy_pandasseries(series)

        r_objects.r('''
                   run_nsdiffs <- function(x,freq, test) {
                            library(forecast)

                            xts = ts(x, frequency=freq)

                            return(nsdiffs(xts, test=test))
                    }
                    ''')

        r_nsdiffs_func = r_objects.globalenv['run_nsdiffs']
        n_diffs = r_nsdiffs_func(series_rpy, frequency, test)
        n_diffs = int(n_diffs[0])
        pandas2ri.deactivate()

        return n_diffs

    @staticmethod
    def r_ndiffs(series: pd.Series,
                 test: str,
                 test_type: str):
        assert test_type in TEST_TYPES, 'unkn type'

        pandas2ri.activate()

        series_rpy = pandas2ri.py2rpy_pandasseries(series)

        r_objects.r('''
                       run_ndiffs <- function(x,test, test_type) {
                                library(forecast)

                                return(ndiffs(x, test=test,type=test_type))
                        }
                        ''')

        r_ndiffs_func = r_objects.globalenv['run_ndiffs']
        n_diffs = r_ndiffs_func(series_rpy, test, test_type)
        n_diffs = int(n_diffs[0])
        pandas2ri.deactivate()

        return n_diffs
