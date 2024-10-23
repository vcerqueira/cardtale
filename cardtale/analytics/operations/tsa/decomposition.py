import pandas as pd
from statsmodels.tsa.seasonal import STL


def get_stl_components(series: pd.Series, period: int, add_residuals: bool = False) -> pd.DataFrame:
    """

    :param series:
    :param period:
    :param add_residuals:
    :return:
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
