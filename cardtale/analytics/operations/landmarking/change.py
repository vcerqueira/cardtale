from mlforecast import MLForecast
from utilsforecast.feature_engineering import trend

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.operations.landmarking.base import Landmarks
from cardtale.analytics.operations.landmarking.config import EXPERIMENT_MODES, MODEL, N_WINDOWS
from cardtale.core.config.freq import HORIZON_BY_FREQUENCY, LAGS_BY_FREQUENCY


class ChangeLandmarks(Landmarks):
    """
    Class for running landmark experiments on change detection in time series data.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
    """

    TEST_NAME = 'change'

    def __init__(self, tsd: TimeSeriesData, change_point: int):
        """
        Initializes the ChangeLandmarks with the given time series data.

        Args:
            tsd (TimeSeriesData): Time series data object.
        """

        super().__init__(tsd=tsd, test_name=self.TEST_NAME)

        self.change_point = change_point

    def run_mlf_cv(self, config_name: str):
        """
        Runs cross-validation using MLForecast for variance experiments.

        Args:
            config_name (str): Name of the configuration to use.

        Returns:
            pd.DataFrame: DataFrame containing the cross-validation results.
        """

        conf = EXPERIMENT_MODES[self.test_name][config_name]

        df = self.tsd.df.copy()

        if conf['step']:
            df, _ = trend(df=df,
                          freq=self.tsd.dt.freq_short,
                          h=0,
                          id_col=self.tsd.id_col,
                          time_col=self.tsd.time_col)

            df['trend'] = (df['trend'] > self.change_point).astype(int)
            df = df.rename(columns={'trend': 'step_change'})
            static_features = []
        else:
            static_features = None

        self.mlf = MLForecast(
            models=MODEL,
            freq=self.tsd.dt.freq_short,
            lags=list(range(1, LAGS_BY_FREQUENCY[self.tsd.dt.freq_short] + 1)),
        )

        cv_df = self.mlf.cross_validation(
            df=df,
            h=HORIZON_BY_FREQUENCY[self.tsd.dt.freq_short],
            n_windows=N_WINDOWS,
            static_features=static_features,
            refit=False,
            id_col=self.tsd.id_col,
            time_col=self.tsd.time_col,
            target_col=self.tsd.target_col,
        )

        return cv_df
