from typing import Dict, Tuple

import pandas as pd

from cardtale.analytics.testing.card.variance import VarianceTesting
from cardtale.core.config.analysis import ALPHA
from cardtale.cards.strings import join_l, gettext


class VarianceTestsParser:
    """
    Class for parsing variance test results and generating analysis text.

    Methods:
        tests_parser(tests: pd.Series) -> str:
            Parses the results of variance tests and generates analysis text.
        performance_parser(show_results: Dict) -> str:
            Parses the performance of variance tests and generates analysis text.
        distr_after_logt(distr_original: str, distr_logt: str) -> str:
            Generates analysis text for distributions after logarithm transformation.
        show_distribution_plot(tests: VarianceTesting) -> Tuple[bool, Dict]:
            Determines which distribution plots to show based on variance test results.
    """

    @staticmethod
    def tests_parser(tests: pd.Series):
        """
        Parses the results of variance tests and generates analysis text.

        Args:
            tests (pd.Series): Series containing the results of variance tests.

        Returns:
            str: Analysis text based on the test results.
        """
        prob_heterosk = tests.mean()

        test_names = tests.index.tolist()
        rej_nms = tests[tests < ALPHA].index.tolist()
        n_rej_nms = tests[tests > ALPHA].index.tolist()

        if prob_heterosk > 0:
            if prob_heterosk == 1:
                analysis_text = gettext('variance_partition_analysis_heterosk_prob_all')
                analysis_text = analysis_text.format(join_l(test_names))
            else:
                analysis_text = gettext('variance_partition_analysis_heterosk_prob_some')
                analysis_text = analysis_text.format(join_l(rej_nms), join_l(n_rej_nms))
        else:
            analysis_text = gettext('variance_partition_analysis_heterosk_prob_none')
            analysis_text = analysis_text.format(join_l(test_names))

        return analysis_text

    @staticmethod
    def performance_parser(show_results: Dict):
        """
        Parses the performance of variance tests and generates analysis text.

        Args:
            show_results (Dict): Dictionary containing the performance results of variance tests.

        Returns:
            str: Analysis text based on the performance results.
        """
        log_improves = show_results['by_log']
        bc_improves = show_results['by_boxcox']

        if log_improves or bc_improves:
            if log_improves and bc_improves:
                analysis_text = gettext('variance_partition_analysis_perf_both')
            else:
                analysis_text = gettext('variance_partition_analysis_perf_one')
                if log_improves:
                    analysis_text = analysis_text.format('logarithm', 'Box-Cox method')
                else:
                    analysis_text = analysis_text.format('Box-Cox method', 'logarithm')
        else:
            analysis_text = gettext('variance_partition_analysis_perf_none')

        return analysis_text

    @classmethod
    def distr_after_logt(cls,
                         distr_original: str,
                         distr_logt: str):
        """
        Generates analysis text for distributions after logarithm transformation.

        Args:
            distr_original (str): Original distribution.
            distr_logt (str): Distribution after logarithm transformation.

        Returns:
            str: Analysis text based on the distributions.
        """

        t = 'Logarithm'

        if distr_original == distr_logt:
            if distr_original is None:
                var_dists_after_t = gettext('variance_dists_equal_and_none').format(t)
            else:
                var_dists_after_t = gettext('variance_dists_equal').format(t, distr_original)
        else:
            if distr_original is None:
                var_dists_after_t = gettext('variance_dists_diff_p1none').format(t, distr_logt)
            elif distr_logt is None:
                var_dists_after_t = gettext('variance_dists_diff_p2none').format(t, distr_original)
            else:
                var_dists_after_t = gettext('variance_dists_diff').format(t, distr_original, distr_logt)

        return var_dists_after_t

    @staticmethod
    def show_distribution_plot(tests: VarianceTesting) -> Tuple[bool, Dict]:
        """
        Determines which distribution plots to show based on variance test results.

        Args:
            tests (VarianceTesting): Object containing the variance test results.

        Returns:
            Tuple[bool, Dict]: Flag indicating whether to show the distribution plots and dictionary of results.
        """
        is_heteroskedastic = tests.prob_heteroskedastic > 0
        log_improves = tests.performance['base'] > tests.performance['log']
        boxcox_improves = tests.performance['base'] > tests.performance['boxcox']
        exists_groupdiff = len(tests.groups_with_diff_var) > 0

        show_results = {
            'by_st': is_heteroskedastic,
            'by_log': log_improves,
            'by_boxcox': boxcox_improves,
            'by_groupdiff': exists_groupdiff,
        }

        show_me = any([*show_results.values()])

        return show_me, show_results
