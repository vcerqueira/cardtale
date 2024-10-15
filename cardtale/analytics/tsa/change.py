from typing import List

import numpy as np
import pandas as pd

# from kats.consts import TimeSeriesData
# from kats.detectors.robust_stat_detection import RobustStatDetector
# from kats.detectors.cusum_detection import CUSUMDetector

from cardtale.visuals.config import INDEX

INDEX_NAME_KATS = 'time'


class ChangeDetection:

    def __init__(self, series: pd.Series):
        self.kats_df = self.get_kats_data_str(series)
        self.n = series.__len__()
        self.window_size = np.sqrt(self.n)

        self.detector = None
        self.change_points = {}

    @staticmethod
    def get_kats_data_str(series: pd.Series):
        series.index.name = INDEX
        df = series.reset_index()

        df = df.rename(columns={INDEX: INDEX_NAME_KATS})

        # return TimeSeriesData(df=df)
        return 0

    def detect_changes(self):
        self.change_points = {
            # 'Robust': self.change.cd_robust(p_value=CHANGE_ALPHA, window_size=window_size),
            'CUSUM': self.cd_cusum(direction=['decrease', 'increase']),
            # 'Bayesian': self.change.cd_bayesian(),
        }

    def cd_cusum(self, direction: List[str]):
        self.detector = 0#CUSUMDetector(self.kats_df)
        # self.change_points = self.detector.detector(change_directions=direction)
        # self.change_points = self.detector.detector(change_directions=direction)

        # return self.change_points
        return []

    def cd_bayesian(self):
        # self.detector = BOCPDetector(self.data)

        # self.change_points = self.detector.detector(
        #    model=BOCPDModelType.NORMAL_KNOWN_MODEL
        # )

        # return self.change_points
        pass

    def cd_robust(self, p_value: float, window_size: int):
        # self.detector = RobustStatDetector(self.kats_df)
        self.detector = 0
        # self.change_points = \
        #     self.detector.detector(p_value_cutoff=p_value,
        #                            comparison_window=window_size)

        # return self.change_points
        return []
