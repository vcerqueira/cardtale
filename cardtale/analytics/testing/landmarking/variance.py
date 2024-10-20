from sklearn.preprocessing import FunctionTransformer, PowerTransformer
from mlforecast import MLForecast
from mlforecast.target_transforms import GlobalSklearnTransformer

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.landmarking.base import Landmarks
from cardtale.analytics.testing.landmarking.config import EXPERIMENT_MODES, MODEL, N_WINDOWS
from cardtale.analytics.tsa.log import LogTransformation
from cardtale.core.config.freq import HORIZON_BY_FREQUENCY, LAGS_BY_FREQUENCY


class VarianceLandmarks(Landmarks):
    TEST_NAME = 'variance'

    def __init__(self, tsd: TimeSeriesData):
        super().__init__(tsd=tsd, test_name=self.TEST_NAME)

    def run_mlf_cv(self, config_name: str):

        conf = EXPERIMENT_MODES[self.test_name][config_name]

        if conf['log']:
            log_transform = FunctionTransformer(func=LogTransformation.transform,
                                                inverse_func=LogTransformation.inverse_transform)

            target_t = [GlobalSklearnTransformer(log_transform)]
        elif conf['boxcox']:
            sk_boxcox = PowerTransformer(method='box-cox', standardize=False)

            target_t = [GlobalSklearnTransformer(sk_boxcox)]
        else:
            target_t = None

        df = self.tsd.df.copy()

        self.mlf = MLForecast(
            models=MODEL,
            freq=self.tsd.dt.freq,
            target_transforms=target_t,
            lags=list(range(1, LAGS_BY_FREQUENCY[self.tsd.dt.freq] + 1)),
        )

        cv_df = self.mlf.cross_validation(
            df=df,
            h=HORIZON_BY_FREQUENCY[self.tsd.dt.freq],
            n_windows=N_WINDOWS,
            refit=False,
        )

        return cv_df
