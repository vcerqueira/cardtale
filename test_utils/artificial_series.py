import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_time_series(
        n_points=365,
        n_series=1,
        frequency='D',
        start_date='2020-01-01',
        base_value=100,
        noise_level=10,
        trend_coef=0,
        seasonal_pattern=None,
        seasonal_amplitude=None,
        variance_increase=False,
        random_seed=None
):
    """
    Generate artificial time series with controllable components.

    Parameters:
    -----------
    n_points : int
        Number of time points to generate
    n_series : int
        Number of distinct time series to generate
    frequency : str
        Frequency of observations ('D' for daily, 'H' for hourly, etc.)
    start_date : str
        Start date in 'YYYY-MM-DD' format
    base_value : float
        Base value for the time series
    noise_level : float
        Standard deviation of the random noise
    trend_coef : float
        Linear trend coefficient (slope)
    seasonal_pattern : str, optional
        Type of seasonality ('daily', 'weekly', 'monthly', 'yearly')
    seasonal_amplitude : float, optional
        Amplitude of seasonal pattern
    variance_increase : bool
        Whether to introduce increasing variance over time
    random_seed : int, optional
        Seed for reproducibility

    Returns:
    --------
    pandas.DataFrame
        DataFrame with columns: unique_id, ds, y
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    # Create date range
    dates = pd.date_range(start=start_date, periods=n_points, freq=frequency)

    # Initialize empty lists for the final DataFrame
    all_dates = []
    all_values = []
    all_ids = []

    for series_id in range(n_series):
        # Generate time components
        t = np.arange(n_points)

        # Base signal: trend + noise
        values = base_value + trend_coef * t + np.random.normal(0, noise_level, n_points)

        # Add seasonality if specified
        if seasonal_pattern and seasonal_amplitude:
            if seasonal_pattern == 'daily':
                period = 24 if frequency == 'H' else 1
            elif seasonal_pattern == 'weekly':
                period = 7 if frequency == 'D' else 168
            elif seasonal_pattern == 'monthly':
                period = 30 if frequency == 'D' else 720
            elif seasonal_pattern == 'yearly':
                period = 365 if frequency == 'D' else 8760
            else:
                raise ValueError("Invalid seasonal pattern")

            seasonal_component = seasonal_amplitude * np.sin(2 * np.pi * t / period)
            values += seasonal_component

        # Add increasing variance if specified
        if variance_increase:
            variance_multiplier = np.linspace(1, 3, n_points)
            values += np.random.normal(0, noise_level * variance_multiplier, n_points)

        # Store results
        all_dates.extend(dates)
        all_values.extend(values)
        all_ids.extend([f'series_{series_id}'] * n_points)

    # Create DataFrame
    df = pd.DataFrame({
        'unique_id': all_ids,
        'ds': all_dates,
        'y': all_values
    })

    return df
