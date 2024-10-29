from typing import Tuple, Dict

from cardtale.cards.strings import gettext
from cardtale.analytics.testing.card.trend import UnivariateTrendTesting


class TrendTestsParser:

    @staticmethod
    def parse_level_prob(tester: UnivariateTrendTesting):
        prob = tester.prob_level

        if prob < 0.3:
            text = 'no evidence'
        elif prob < 0.6:
            text = 'a slight evidence'
        elif prob < 0.9:
            text = 'a reasonable evidence'
        else:
            text = 'a strong evidence'

        return text

    @staticmethod
    def parse_t_performance(tester: UnivariateTrendTesting):

        perf = tester.performance

        t_improves = perf['base'] > perf['trend_feature']

        if t_improves:
            analysis_text = gettext('trend_line_analysis_t_good')
        else:
            analysis_text = gettext('trend_line_analysis_t_bad')

        return analysis_text

    @staticmethod
    def parse_differencing_performance(tester: UnivariateTrendTesting):

        perf = tester.performance

        diff_improves = perf['base'] > perf['first_differences']

        if diff_improves:
            analysis_text = gettext('trend_line_analysis_diff_good')
        else:
            analysis_text = gettext('trend_line_analysis_diff_bad')

        return analysis_text

    @staticmethod
    def show_trend_plots(tester: UnivariateTrendTesting) -> Tuple[bool, Dict]:

        perf = tester.performance

        diff_improves = perf['base'] > perf['first_differences']
        t_improves = perf['base'] > perf['trend_feature']

        show_results = {
            'by_trend': tester.prob_trend > 0,
            'by_level': tester.prob_level > 0,
            'by_diff': diff_improves,
            'by_t': t_improves,
        }

        show_me = any([*show_results.values()])

        return show_me, show_results
