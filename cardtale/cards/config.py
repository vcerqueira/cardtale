from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent / 'cards' / 'templates' / 'html'
STRUCTURE_TEMPLATE = 'structure.html'
CARD_HTML = 'card.html'
TOC_HTML = 'toc.html'

# todo obsolete
FAILED_SECTIONS_TEXT = {
    'trend': 'Several tests were carried out to analyse the trend component. Yet, no significant trend was found.'
             'Taking first differences or feature extraction for trend inclusion did not improve forecasting performance.',
    'seasonality': 'The seasonal component is also not relevant according to the tests carried out.',
    'variance': 'Several heteroskedasticity tests were carried out. But, these did not reject the hypothesis that the time series is homoskedastic. '
                'Besides, common transformations used to stabilize the variance did not improve forecasting performance.',
    'change': 'Finally, no change points were found in the time series.',
}

INCLUDED_SECTIONS_TEXT = {
    'trend': 'Section {} details the analysis of trend. This analysis is split into two parts. '
             'The statistical analysis that described whether the time series is trend-stationary or not are described. '
             'Besides, we test whether some typical transformation used to deal with trend lead to better forecasting performance.',
    'seasonality': 'The seasonal component is analised in Section {}. Several statistical tests are carried out for different seasonal periods. '
                   'These evaluate not only seasonal stationarity but also statistical differences among seasonal groups.'
                   ' Finally, tentative experimental results are reported which indicate possible directions for modeling seasonality.',
    'variance': 'Section {} presents the analysis of the variance. '
                'Different heteroskedasticity tests are carried out.'
                ' Besides these, experiments are performed to assess whether transforming the data improves forecasting performance.',
    'change': 'Finally, change detection results are described in Section {}. The distribution of the data is analysed before and after change occurs.',
}

OMITTED_SECTION_HEADER_NAME = 'Report Organization'
