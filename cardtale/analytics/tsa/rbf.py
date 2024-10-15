import pandas as pd

from sklego.preprocessing import RepeatingBasisFunction

PERIOD_NOT_AVAILABLE_ERROR = 'Period not available.'
DATETIME_INDEX_ERROR = 'index should be a pd.DatetimeIndex object'

# todo remove this one---maybe add later
class RBFTerms:
    """
    This is a class for repeating basis functions

    Extracting seasonal information using repeating basis functions

    Attributes:
        n (int): Number of data points
        period (int): target period
        n_terms (int): Number of terms
        prefix (str): Prefix to include in the columns
        model (str): Model to create new columns from base series
    """

    AVAILABLE_PERIODS = [
        '.month',
        '.quarter',
        '.day',
        '.hour',
        '.dayofweek',
        '.year'
        # '.weekofyear',
        # '.dayofyear'
    ]

    PERIOD_RANGES = {
        '.month': (1, 12),
        '.quarter': (1, 4),
        '.day': (1, 31),
        '.hour': (0, 23),
        '.dayofweek': (0, 6),
        '.year': (1970, 2024),
        # '.weekofyear',
        # '.dayofyear'
    }

    def __init__(self, n_terms: int, period: str, prefix: str = ''):
        assert period in self.AVAILABLE_PERIODS, PERIOD_NOT_AVAILABLE_ERROR

        self.period = period
        self.n_terms = n_terms
        self.prefix = prefix
        self.model = RepeatingBasisFunction(n_periods=n_terms,
                                            column='index',
                                            input_range=self.PERIOD_RANGES[self.period],
                                            remainder='drop')

    def fit(self, index: pd.DatetimeIndex):
        """
        Fitting the RBF transformer

        Parameters:
        index (pd.DatetimeIndex): Index of a time series

        Returns:
        self: Fitted transformer
        """

        index_df = self.prepare_index_df(index)

        self.model.fit(index_df)

    def transform(self, index: pd.DatetimeIndex):
        """
        Transforming the index to a set of predictor variables

        Parameters:
        index (pd.DatetimeIndex): Index of a time series

        Returns:
        pd.DataFrame: set of predictor variables
        """

        index_df = self.prepare_index_df(index)

        feats = self.model.transform(index_df)

        col_names = [f'{self.prefix}RBT{i}' for i in range(feats.shape[1])]

        feats = pd.DataFrame(feats, columns=col_names, index=index)

        return feats

    def prepare_index_df(self, index: pd.DatetimeIndex):
        """
        Getting the respective period from the index

        Parameters:
        index (pd.DatetimeIndex): Index of a time series

        Returns:
        pd.DataFrame: data relative to a specific granularity (e.g. month)
        """

        assert isinstance(index, pd.DatetimeIndex), DATETIME_INDEX_ERROR

        df = pd.DataFrame({'index': eval(f'index{self.period}')})

        return df
