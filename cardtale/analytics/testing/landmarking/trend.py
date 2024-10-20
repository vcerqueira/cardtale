from mlforecast import MLForecast
from mlforecast.target_transforms import Differences
from utilsforecast.feature_engineering import trend

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.landmarking.base import Landmarks
from cardtale.core.config.freq import HORIZON_BY_FREQUENCY, LAGS_BY_FREQUENCY
from cardtale.analytics.testing.landmarking.config import EXPERIMENT_MODES, MODEL, N_WINDOWS


class TrendLandmarks(Landmarks):
    TEST_NAME = 'trend'

    def __init__(self, tsd: TimeSeriesData):
        super().__init__(tsd=tsd, test_name=self.TEST_NAME)

    def run_mlf_cv(self, config_name: str):

        conf = EXPERIMENT_MODES[self.test_name][config_name]

        if conf['first_diff']:
            target_t = [Differences([1])]
        else:
            target_t = None

        if conf['trend_feature']:
            df, _ = trend(df=self.tsd.df,
                          freq=self.tsd.dt.freq,
                          h=0,
                          id_col=self.tsd.id_col,
                          time_col=self.tsd.time_col)
        else:
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
