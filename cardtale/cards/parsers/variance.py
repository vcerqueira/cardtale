from typing import Dict, Tuple

import pandas as pd

from cardtale.analytics.testing.card.variance import VarianceTesting
from cardtale.core.config.analysis import ALPHA
from cardtale.cards.strings import join_l, gettext


class VarianceTestsParser:

    @staticmethod
    def tests_parser(tests: pd.Series):
        """
        :param tests: tests attribute from VarianceTesting
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
        :param show_results: show_results attribute from VarianceShowTests.show_distribution_plot
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
        :param distr_original:
        :param distr_logt:
        :param show_results: show_results attribute from VarianceShowTests.show_distribution_plot
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
        show_me, show_results = VarianceShowTests.show_distribution_plot(ds.tests.variance)

        :param tests: VarianceTesting object
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
