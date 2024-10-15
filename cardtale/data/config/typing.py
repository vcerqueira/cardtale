from typing import Optional, Union
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV

LearningAlgorithm = Union[RandomForestRegressor, RidgeCV]

Period = Optional[Union[float, int]]
