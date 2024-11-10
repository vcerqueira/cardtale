import lightgbm as lgb

N_TERMS = 3
TEST_SIZE = 0.2
N_WINDOWS = 1  # 5
MODEL = {'lgb': lgb.LGBMRegressor(verbosity=-1)}

EXPERIMENT_MODES = {
    'trend': {
        'base': {'trend_feature': False, 'first_diff': False, 'log_diff': False},  # t as feature
        'trend_feature': {'trend_feature': True, 'first_diff': False, 'log_diff': False},  # t as feature
        'first_differences': {'trend_feature': False, 'first_diff': True, 'log_diff': False},  # first differences
        'log_differences': {'trend_feature': False, 'first_diff': False, 'log_diff': True},  # log differences
        'both': {'trend_feature': True, 'first_diff': True, 'log_diff': False},
    },
    'seasonality': {
        'base': {'fourier': False, 'seasonal_differences': False},
        'fourier': {'fourier': True, 'seasonal_differences': False},
        'seas_diffs': {'fourier': False, 'seasonal_differences': True},
        'both': {'fourier': True, 'seasonal_differences': True},
    },
    'variance': {
        'base': {'log': False, 'boxcox': False},
        'log': {'log': True, 'boxcox': False},
        'boxcox': {'log': False, 'boxcox': True},
    },
    'change': {
        'base': {'step': False},
        'step': {'step': True},
    },
}
