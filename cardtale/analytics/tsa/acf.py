from typing import List

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf, pacf

from cardtale.core.utils.categories import as_categorical


class AutoCorrelation:
    PARAMS = {
        'bartlett_confint': True,
        'adjusted': False,
        'missing': 'none',
    }

    def __init__(self, n_lags: int, alpha: float):
        self.n_lags = n_lags
        self.alpha = alpha
        self.significance_thr = 0
        self.acf = None
        self.acf_df = None
        self.conf_int = None
        self.acf_analysis = {}

    def calc_acf(self, data: pd.Series):
        self.significance_thr = 2 / np.sqrt(len(data))

        acf_x = acf(
            data,
            nlags=self.n_lags,
            alpha=self.alpha,
            **self.PARAMS
        )

        self.acf, self.conf_int = acf_x[:2]

        self.acf_df = pd.DataFrame({
            'ACF': self.acf,
            'ACF_low': self.conf_int[:, 0],
            'ACF_high': self.conf_int[:, 1],
        })

        self.acf_df['Lag'] = ['t'] + [f't-{i}' for i in range(1, self.n_lags + 1)]
        self.acf_df['Lag'] = as_categorical(self.acf_df, 'Lag')

    def calc_pacf(self, data: pd.Series):
        self.significance_thr = 2 / np.sqrt(len(data))

        acf_x = pacf(
            data,
            nlags=self.n_lags,
            alpha=self.alpha
        )

        self.acf, self.conf_int = acf_x[:2]

        self.acf_df = pd.DataFrame({
            'ACF': self.acf,
            'ACF_low': self.conf_int[:, 0],
            'ACF_high': self.conf_int[:, 1],
        })

        self.acf_df['Lag'] = ['t'] + [f't-{i}' for i in range(1, self.n_lags + 1)]
        self.acf_df['Lag'] = as_categorical(self.acf_df, 'Lag')

    def significance_analysis(self, period: int):
        """
        todo autoseasonality -> so faz sentido se remover a sazonalidade
        mas para isso ja tenho os testes mais a frente...
        :param period:
        :return:
        """

        raw_seasonality = []
        for i, _int in enumerate(self.conf_int):
            if _int[0] >= 0 and i > 1:
                raw_seasonality.append(i)

        seasonal_lags = {}
        for i in range(1, 5):
            try:
                seasonal_lags[i * period] = self.acf[[i * period]][0]
            except IndexError:
                break

        self.acf_analysis['seasonal_lags'] = pd.Series(seasonal_lags)
        self.acf_analysis['seasonal_lags_sig'] = self.acf_analysis['seasonal_lags'] > self.significance_thr
        self.acf_analysis['auto_seasonality'] = self._get_seasonality_length(raw_seasonality)
        self.acf_analysis['significant_ids'] = np.argwhere(np.abs(self.acf) > self.significance_thr).flatten()
        self.acf_analysis['significant_ids'] = [x for x in self.acf_analysis['significant_ids'] if x != 0]
        self.acf_analysis['under_thr_ids'] = np.argwhere(self.acf < -self.significance_thr).flatten()
        self.acf_analysis['over_thr_ids'] = np.argwhere(self.acf > self.significance_thr).flatten()
        self.acf_analysis['over_thr_ids'] = [x for x in self.acf_analysis['over_thr_ids'] if x != 0]

    @staticmethod
    def _get_seasonality_length(d: List[int]) -> List[int]:
        out = []
        while d:
            k = d.pop(0)
            d = [i for i in d if i % k != 0]
            out.append(k)
        return out
