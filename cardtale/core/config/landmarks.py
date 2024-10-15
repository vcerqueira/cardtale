from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV

N_LAGS = 2
HORIZON = 1
SHUFFLE = False
TEST_SIZE = 0.2
N_TERMS = 3

MODELS = {
    'RF': RandomForestRegressor,
    'Ridge': RidgeCV,
}

LEARNING_ALGORITHM = 'Ridge'

MODEL = MODELS[LEARNING_ALGORITHM]()

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
