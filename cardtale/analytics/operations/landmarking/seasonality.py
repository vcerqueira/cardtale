from typing import Optional

from mlforecast import MLForecast
from mlforecast.target_transforms import Differences
from utilsforecast.feature_engineering import fourier, time_features

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.operations.landmarking.base import Landmarks
from cardtale.core.config.freq import HORIZON_BY_FREQUENCY, LAGS_BY_FREQUENCY, TIME_FEATURES_FREQ
from cardtale.analytics.operations.landmarking.config import EXPERIMENT_MODES, MODEL, N_WINDOWS, N_TERMS


class SeasonalLandmarks(Landmarks):
    """
    Class for running landmark experiments on seasonality in time series data.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        target_period (int): Target period for seasonal decomposition.
    """

    TEST_NAME = 'seasonality'

    def __init__(self, tsd: TimeSeriesData, target_period: Optional[int] = None):
        """
        Initializes the SeasonalLandmarks with the given time series data and target period.

        Args:
            tsd (TimeSeriesData): Time series data object.
            target_period (Optional[int]): Target period for seasonal decomposition. Defaults to None.
        """

        if target_period is not None:
            self.target_period = target_period
        else:
            self.target_period = self.tsd.period

        super().__init__(tsd=tsd, test_name=self.TEST_NAME)

    def run_mlf_cv(self, config_name: str):
        """
        Runs cross-validation using MLForecast for seasonality experiments.

        Args:
            config_name (str): Name of the configuration to use.

        Returns:
            pd.DataFrame: DataFrame containing the cross-validation results.
        """

        conf = EXPERIMENT_MODES[self.test_name][config_name]

        if conf['seasonal_differences']:
            target_t = [Differences([self.target_period])]
        else:
            target_t = None

        df_ = self.tsd.df.copy()

        if conf['fourier']:
            df, _ = fourier(df=df_,
                            freq=self.tsd.dt.freq_short,
                            season_length=self.target_period,
                            k=N_TERMS,
                            h=0)
            static_features = []
        elif conf['time_features']:
            feats_ = TIME_FEATURES_FREQ[self.tsd.dt.freq_short][self.target_period]

            df, _ = time_features(df=df_,
                                  freq=self.tsd.dt.freq_short,
                                  h=0,
                                  features=feats_)
            static_features = []
        else:
            df = df_.copy()
            static_features = None

        self.mlf = MLForecast(
            models=MODEL,
            freq=self.tsd.dt.freq_short,
            target_transforms=target_t,
            lags=list(range(1, LAGS_BY_FREQUENCY[self.tsd.dt.freq_short] + 1)),
        )

        cv_df = self.mlf.cross_validation(
            df=df,
            h=HORIZON_BY_FREQUENCY[self.tsd.dt.freq_short],
            n_windows=N_WINDOWS,
            refit=False,
            static_features=static_features
        )

        return cv_df
