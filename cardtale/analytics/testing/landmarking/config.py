import lightgbm as lgb
from sklearn.linear_model import RidgeCV

N_TERMS = 3

EXPERIMENT_MODES = {
    'trend': {
        'base': {'T': False, 'n_diffs': 0},  # t as feature
        'T_feature': {'T': True, 'n_diffs': 0},  # t as feature
        'diff_1': {'T': False, 'n_diffs': 1},  # first differences
        'both': {'T': True, 'n_diffs': 1},
    },
    'seasonality': {
        'base': {'fourier': False, 'rbf': False},
        'both': {'fourier': True, 'rbf': True},
    },
    'variance': {
        'base': {'log': False, 'boxcox': False},
        'log': {'log': True, 'boxcox': False},
        'boxcox': {'log': False, 'boxcox': True},
    },
}
