import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL
from statsmodels.stats.diagnostic import acorr_ljungbox#, acorr_breusch_godfrey


class DecompositionSTL:

    @staticmethod
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

    @staticmethod
    def seasonal_strength(seasonal: pd.Series, residuals: pd.Series):
        assert seasonal.index.equals(residuals.index)

        # variance of residuals + seasonality
        resid_seas_var = (residuals + seasonal).var()
        # variance of residuals
        resid_var = residuals.var()

        # seasonal strength
        result = 1 - (resid_var / resid_seas_var)
        result = max(0, result)
        result = np.round(result, 2)

        return result

    @staticmethod
    def trend_strength(trend: pd.Series, residuals: pd.Series):
        assert trend.index.equals(residuals.index)

        # variance of residuals + trend
        resid_trend_var = (residuals + trend).var()
        # variance of residuals
        resid_var = residuals.var()

        # seasonal strength
        result = 1 - (resid_var / resid_trend_var)
        result = max(0, result)
        result = np.round(result, 2)

        return result

    @staticmethod
    def residuals_ljung_box(residuals: pd.Series, n_lags: int):
        lb_test = acorr_ljungbox(residuals, lags=n_lags)

        auto_corr_exists = lb_test['lb_pvalue'] < 0.01

        avg_resid = residuals.mean().round(2)
        med_resid = residuals.median().round(2)

        resid_str = {
            'auto_corr_exists': auto_corr_exists,
            'auto_corr_exists_avg': auto_corr_exists.mean(),
            'avg_resid': avg_resid,
            'med_resid': med_resid,
            'positive_pct': ((residuals > 0).mean() * 100).round(2),
            'negative_pct': ((residuals < 0).mean() * 100).round(2),
            'pos_mean': residuals[residuals > 0].mean().round(3),
            'neg_mean': residuals[residuals < 0].mean().round(3)
        }

        if np.abs(resid_str['positive_pct'] - 50) < 5:
            resid_str['behaviour'] = 'balanced'
        else:
            resid_str['behaviour'] = 'unbalanced'

        return resid_str
