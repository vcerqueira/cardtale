from typing import Tuple, Dict

from cardtale.cards.strings import gettext
from cardtale.analytics.testing.card.trend import UnivariateTrendTesting


class TrendTestsParser:
    """
    Class for parsing trend test results and generating analysis text.

    Methods:
        parse_level_prob(tester: UnivariateTrendTesting) -> str:
            Parses the probability level of the trend and generates analysis text.
        parse_t_performance(tester: UnivariateTrendTesting) -> str:
            Parses the performance of the trend feature and generates analysis text.
        parse_differencing_performance(tester: UnivariateTrendTesting) -> str:
            Parses the performance of the first differences and generates analysis text.
        show_trend_plots(tester: UnivariateTrendTesting) -> Tuple[bool, Dict]:
            Determines which trend plots to show based on test results.
    """

    @staticmethod
    def parse_level_prob(tester: UnivariateTrendTesting):
        """
        Parses the probability level of the trend and generates analysis text.

        Args:
            tester (UnivariateTrendTesting): Object containing the trend test results.

        Returns:
            str: Analysis text based on the probability level.
        """
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
        """
        Parses the performance of the trend feature and generates analysis text.

        Args:
            tester (UnivariateTrendTesting): Object containing the trend test results.

        Returns:
            str: Analysis text based on the trend feature performance.
        """

        perf = tester.performance

        t_improves = perf['base'] > perf['trend_feature']

        if t_improves:
            analysis_text = gettext('trend_line_analysis_t_good')
        else:
            analysis_text = gettext('trend_line_analysis_t_bad')

        return analysis_text

    @staticmethod
    def parse_differencing_performance(tester: UnivariateTrendTesting):
        """
        Parses the performance of the first differences and generates analysis text.

        Args:
            tester (UnivariateTrendTesting): Object containing the trend test results.

        Returns:
            str: Analysis text based on the first differences performance.
        """

        perf = tester.performance

        diff_improves = perf['base'] > perf['first_differences']

        if diff_improves:
            analysis_text = gettext('trend_line_analysis_diff_good')
        else:
            analysis_text = gettext('trend_line_analysis_diff_bad')

        return analysis_text

    @staticmethod
    def show_trend_plots(tester: UnivariateTrendTesting) -> Tuple[bool, Dict]:
        """
        Determines which trend plots to show based on test results.

        Args:
            tester (UnivariateTrendTesting): Object containing the trend test results.

        Returns:
            Tuple[bool, Dict]: Flag indicating whether to show the trend plots and dictionary of results.
        """

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
