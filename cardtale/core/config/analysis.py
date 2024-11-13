TREND_STRENGTH_INTERVAL = {
    'strong': 0.6,
    'moderate': 0.3,
    'slight': 0,
}

GOLDFELD_Q_PARTITION = 0.33

ALPHA = 0.05

ROUND_N = 2
STATS_TO_ROUND = ['mean', '50%', 'std', 'min', 'max']

DECOMPOSITION_METHOD = 'STL (Season-Trend decomposition using LOESS)'
DECOMPOSITION_METHOD_SHORT = 'STL'
CORRELATION_TESTS = ['pearson', 'kendall', 'spearman']
MEAN_TEST = 'Kruskal-Wallis'
VAR_TEST = "Levene's"
