import pandas as pd

AVAILABLE_FREQ = {
    'H': 'Hourly',
    'D': 'Daily',
    'W': 'Weekly',
    'M': 'Monthly',
    'ME': 'Monthly',
    'MS': 'Monthly',
    'Q': 'Quarterly',
    'QE': 'Quarterly',
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
    'QE': 6,
    'QS': 6,
    'Y': 3,
}

LAGS_BY_FREQUENCY = {k: int(v * 1.25) for k, v in HORIZON_BY_FREQUENCY.items()}

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
    'ME': {'format': '%Y-%m',
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
    'QE': {'format': '%Y-%U',
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
           'main_period': ['N/A'],
           'main_period_int': 1,
           'main_period_name': ['N/A'], },
}

SEASONS = {
    1: 'Winter',
    2: 'Spring',
    3: 'Summer',
    4: 'Autumn',
}

# units that appear in plots
# e.g. monthly time series have
### monthly (month-by-month),
### and quarterly (quarter-by-quarter) units
# FREQUENCY_TABLE_UNITS = {
#     'H': ['Hourly', 'Daily', 'Weekly', 'Monthly'],
#     'D': ['Daily', 'Weekly', 'Monthly'],
#     'W': ['Weekly', 'Monthly', 'Quarterly'],
#     'M': ['Monthly', 'Quarterly'],
#     'ME': ['Monthly', 'Quarterly'],
#     'MS': ['Monthly', 'Quarterly'],
#     'Q': ['Quarterly'],
#     'QE': ['Quarterly'],
#     'QS': ['Quarterly'],
#     'Y': ['N/A'],
# }

PLOTTING_SEAS_CONFIGS = {
    'hourly': [{'base': 'Hour', 'name': 'Daily', 'main': True, 'period': 24, 'group_tests': False},
               {'base': 'Week', 'name': 'Weekly', 'main': False, 'period': 52 * 24, 'group_tests': True},
               {'base': 'Hour', 'name': 'Hourly', 'main': False, 'period': None, 'group_tests': True}],

    'daily': [{'base': 'Day', 'name': 'Weekly', 'main': True, 'period': 7, 'group_tests': True},
              {'base': 'Month', 'name': 'Monthly', 'main': False, 'period': 30, 'group_tests': True},
              {'base': 'Day', 'name': 'Daily', 'main': False, 'period': None, 'group_tests': False}],

    'weekly': [{'base': 'Week', 'name': 'Yearly', 'main': True, 'period': 52, 'group_tests': False},
               {'base': 'Month', 'name': 'Monthly', 'main': False, 'period': 4, 'group_tests': True},
               {'base': 'Week', 'name': 'Weekly', 'main': False, 'period': None, 'group_tests': True}],

    'monthly': [{'base': 'Month', 'name': 'Yearly', 'main': True, 'period': 12, 'group_tests': False},
                {'base': 'Quarter', 'name': 'Quarterly', 'main': False, 'period': 4, 'group_tests': True},
                {'base': 'Month', 'name': 'Monthly', 'main': False, 'period': None, 'group_tests': True}],

    'quarterly': [{'base': 'Quarter', 'name': 'Yearly', 'main': True, 'period': 4, 'group_tests': False},
                  {'base': 'Quarter', 'name': 'Quarterly', 'main': False, 'period': None, 'group_tests': True}],
    'yearly': None,

}

FREQUENCIES = [*FREQUENCY_TABLE]

FREQ_TAB = pd.DataFrame(FREQUENCY_TABLE).T

FREQUENCY_INT_DICT = {
    'min': {'min': 0,
            'H': 60,
            'D': 60 * 24,
            'W': 60 * 24 * 7,
            'MS': 0,
            'ME': 0,
            'QS': 0,
            'QE': 0,
            'YS': 0},
    'H': {'min': 0,
          'H': 0,
          'D': 24,
          'W': 24 * 7,
          'MS': 24 * 7 * 30.5,
          'ME': 24 * 7 * 30.5,
          'QS': 24 * 7 * 30.5 * 3,
          'QE': 24 * 7 * 30.5 * 3,
          'YS': 24 * 7 * 30.5 * 3 * 4},
    'D': {'min': 0,
          'H': 0,
          'D': 0,
          'W': 7,
          'MS': 30.5,
          'ME': 30.5,
          'QS': 365.25 / 4,
          'QE': 365.25 / 4,
          'YS': 365.25},
    'W': {'min': 0,
          'H': 0,
          'D': 0,
          'W': 0,
          'MS': 4.35,
          'ME': 4.35,
          'QS': 4.35 * 4,
          'QE': 4.35 * 4,
          'YS': 52.2},
    'MS': {'min': 0, 'H': 0, 'D': 0, 'W': 0, 'MS': 0, 'ME': 0, 'QS': 4, 'QE': 4, 'YS': 12},
    'ME': {'min': 0, 'H': 0, 'D': 0, 'W': 0, 'MS': 0, 'ME': 0, 'QS': 4, 'QE': 4, 'YS': 12},
    'QS': {'min': 0, 'H': 0, 'D': 0, 'W': 0, 'MS': 0, 'ME': 0, 'QS': 0, 'QE': 0, 'YS': 4},
    'QE': {'min': 0, 'H': 0, 'D': 0, 'W': 0, 'MS': 0, 'ME': 0, 'QS': 0, 'QE': 0, 'YS': 4},
    'YS': {'min': 0, 'H': 0, 'D': 0, 'W': 0, 'MS': 0, 'ME': 0, 'QS': 0, 'QE': 0, 'YS': 0},
}

FREQ_INT_DF = pd.DataFrame(FREQUENCY_INT_DICT)

TIME_FEATURES_FREQ = {
    'ME': {
        12: ['month'],
        4: ['quarter'],
    },
    'MS': {
        12: ['month'],
        4: ['quarter'],
    },
    'M': {
        12: ['month'],
        4: ['quarter'],
    }
}
