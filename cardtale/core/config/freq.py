import pandas as pd

AVAILABLE_FREQ = {
    'H': 'Hourly',
    'D': 'Daily',
    'W': 'Weekly',
    'M': 'Monthly',
    'ME': 'Monthly',
    'MS': 'Monthly',
    'Q': 'Quarterly',
    'QS': 'Quarterly',
    'Y': 'Yearly',
}

HORIZON_BY_FREQUENCY = {
    'H': 24,
    'D': 14,
    'W': 8,
    'M': 12,
    'ME': 12,
    'MS': 12,
    'Q': 6,
    'QS': 6,
    'Y': 3,
}

LAGS_BY_FREQUENCY = {k: int(HORIZON_BY_FREQUENCY[k] * 1.25) for k in HORIZON_BY_FREQUENCY}

MONTH_LIST = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]

FREQUENCY_TABLE = {
    'min': {'format': '%Y-%m-%d %H:%M',
            'format_pretty': '%Y-%m-%d %H:%M',
            'name': 'Minutely',
            'index': '.minute',
            'main_period': ['H'],
            'main_period_int': 60,
            'main_period_name': ['Hourly'], },
    'H': {'format': '%Y-%m-%d %H',
          'format_pretty': '%Y-%m-%d %H',
          'name': 'Hourly',
          'index': '.hour',
          'main_period': ['D'],
          'main_period_int': 24,
          'main_period_name': ['Daily'], },
    'D': {'format': '%Y-%m-%d',
          'format_pretty': '%Y-%m-%d',
          'name': 'Daily',
          'index': '.day',
          'main_period': ['W', 'MS', 'YS'],
          'main_period_int': 7,
          'main_period_name': ['Weekly', 'Monthly', 'Yearly'], },
    'W': {'format': '%Y-%U',
          'format_pretty': '%Y Week-%U',
          'name': 'Weekly',
          'index': '.week',
          'main_period': ['MS', 'YS'],
          'main_period_int': 52,
          'main_period_name': ['Monthly', 'Yearly'], },
    'MS': {'format': '%Y-%m',
           'format_pretty': '%B %Y',
           'name': 'Monthly',
           'index': '.month',
           'main_period': ['YS'],
           'main_period_int': 12,
           'main_period_name': ['Yearly'], },
    'QS': {'format': '%Y-%U',
           'format_pretty': '%Y-%U',
           'name': 'Quarterly',
           'index': '.quarter',
           'main_period': ['YS'],
           'main_period_int': 4,
           'main_period_name': ['Yearly'], },
    'YS': {'format': '%Y',
           'format_pretty': '%Y',
           'name': 'Yearly',
           'index': '.year',
           'main_period': ['???'],
           'main_period_int': 1,
           'main_period_name': ['???'], },
}

SEASONS = {
    1: 'Winter',
    2: 'Spring',
    3: 'Summer',
    4: 'Autumn',
}

FREQUENCIES = [*FREQUENCY_TABLE]

FREQ_TAB = pd.DataFrame(FREQUENCY_TABLE).T

FREQUENCY_INT_DICT = {
    'min': {'min': 0,
            'H': 60,
            'D': 60 * 24,
            'W': 60 * 24 * 7,
            'MS': 0,
            'QS': 0,
            'YS': 0},
    'H': {'min': 0,
          'H': 0,
          'D': 24,
          'W': 24 * 7,
          'MS': 24 * 7 * 30.5,
          'QS': 24 * 7 * 30.5 * 3,
          'YS': 24 * 7 * 30.5 * 3 * 4},
    'D': {'min': 0,
          'H': 0,
          'D': 0,
          'W': 7,
          'MS': 30.5,
          'QS': 365.25 / 4,
          'YS': 365.25},
    'W': {'min': 0,
          'H': 0,
          'D': 0,
          'W': 0,
          'MS': 4.35,
          'QS': 4.35 * 4,
          'YS': 52.2},
    'MS': {'min': 0, 'H': 0, 'D': 0, 'W': 0, 'MS': 0, 'QS': 4, 'YS': 12},
    'QS': {'min': 0, 'H': 0, 'D': 0, 'W': 0, 'MS': 0, 'QS': 0, 'YS': 4},
    'YS': {'min': 0, 'H': 0, 'D': 0, 'W': 0, 'MS': 0, 'QS': 0, 'YS': 0},
}

FREQ_INT_DF = pd.DataFrame(FREQUENCY_INT_DICT)
