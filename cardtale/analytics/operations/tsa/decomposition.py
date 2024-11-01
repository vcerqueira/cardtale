import pandas as pd
from statsmodels.tsa.seasonal import STL


def get_stl_components(series: pd.Series,
                       period: int,
                       add_residuals: bool = True) -> pd.DataFrame:

    """
    Decomposes a time series into trend, seasonal, and optionally residual components using STL.

    Args:
        series (pd.Series): Time series data.
        period (int): Period for seasonal decomposition.
        add_residuals (bool, optional): Flag to include residuals in the output. Defaults to False.

    Returns:
        pd.DataFrame: DataFrame containing the decomposed components.
    """

    ts_decomp = STL(series, period=period).fit()

    components = {
        'Trend': ts_decomp.trend,
        'Seasonal': ts_decomp.seasonal,
    }

    if add_residuals:
        components['Residuals'] = ts_decomp.resid

    components_df = pd.DataFrame(components).reset_index()

    return components_df
