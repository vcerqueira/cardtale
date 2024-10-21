import pandas as pd
from mlforecast import MLForecast
from datasetsforecast.losses import smape
from utilsforecast.evaluation import evaluate
from datasetsforecast.evaluation import accuracy

from cardtale.core.data import TimeSeriesData
from cardtale.core.config.freq import HORIZON_BY_FREQUENCY, LAGS_BY_FREQUENCY
from cardtale.analytics.testing.landmarking.config import EXPERIMENT_MODES, MODEL, N_WINDOWS

UNKNOWN_TEST_ERROR = 'Unknown experiment type'


class Landmarks:
    TEST_NAME = ''

    def __init__(self, test_name: str, tsd: TimeSeriesData):

        assert test_name in [*EXPERIMENT_MODES], UNKNOWN_TEST_ERROR

        self.test_name = test_name
        self.tsd = tsd

        self.mlf = None
        self.results = {}
        self.importance = {}

    def run(self):
        for conf in EXPERIMENT_MODES[self.test_name]:
            cv_df = self.run_mlf_cv(conf)
            error = self.score_cv(cv_df)

            self.results[conf] = error

    def run_mlf_cv(self, config_name: str):

        if config_name == "":
            self.mlf = MLForecast(
                models=MODEL,
                freq=self.tsd.dt.freq,
                # target_transforms=[Differences([1])],
                # target_transforms=[GlobalSklearnTransformer(sk_log1p)],
                lags=list(range(1, LAGS_BY_FREQUENCY[self.tsd.dt.freq] + 1)),
                # date_features=['month', 'hour', 'dayofweek']
            )

        cv_df = self.mlf.cross_validation(
            df=self.tsd.df,
            h=HORIZON_BY_FREQUENCY[self.tsd.dt.freq],
            n_windows=N_WINDOWS,
            refit=False,
        )

        return cv_df

    def score_cv(self, cv_df: pd.DataFrame):

        evaluation_df = accuracy(cv_df.drop(columns=['cutoff']),
                                 metrics=[smape],
                                 id_col=self.tsd.id_col,
                                 agg_by=[self.tsd.id_col])

        score = evaluation_df.drop(columns=['metric', self.tsd.id_col]).mean()[[*MODEL][0]]

        return score
