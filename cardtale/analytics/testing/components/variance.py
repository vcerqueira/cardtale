from typing import Dict, Tuple

import pandas as pd

from cardtale.analytics.tsa.heteroskedasticity import het_tests, HETEROSKEDASTICITY_TESTS
from cardtale.analytics.testing.landmarking.variance import VarianceLandmarks
from cardtale.analytics.testing.components.base import Tester
from cardtale.analytics.testing.preprocess.log import LogTransformation
from cardtale.analytics.testing.preprocess.boxcox import BoxCox
from cardtale.analytics.tsa.distributions import KolmogorovSmirnov

from cardtale.cards.strings import join_l, gettext
from cardtale.data.config.analysis import ALPHA


class VarianceTesting(Tester):

    def __init__(self, series: pd.Series):
        super().__init__(series)

        self.prob_heteroskedastic: float = -1
        self.group_var = []
        self.residuals = None

    def run_statistical_tests(self):
        for k in HETEROSKEDASTICITY_TESTS:
            try:
                self.tests[HETEROSKEDASTICITY_TESTS[k]], self.residuals = \
                    het_tests(self.series, k, return_residuals=True)
            except ValueError:
                continue

        self.tests = pd.Series(self.tests)
        self.tests = (self.tests < ALPHA).astype(int)

        self.prob_heteroskedastic = self.tests.mean()

    def run_landmarks(self):

        var_lm = VarianceLandmarks()
        var_lm.make_tests(self.series)

        self.performance = var_lm.results

    @staticmethod
    def variance_st_tests_parser(tests: pd.Series):
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
    def variance_perf_parser(show_results: Dict):
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

    @staticmethod
    def variance_dists_after_transformation_choice(show_results: Dict):
        """
        :param show_results: show_results attribute from VarianceShowTests.show_distribution_plot
        """
        log_improves = show_results['by_log']
        bc_improves = show_results['by_boxcox']

        if log_improves or bc_improves:
            if log_improves and bc_improves:
                transformation = 'Logarithm'
            else:
                if log_improves:
                    transformation = 'Logarithm'
                else:
                    transformation = 'Box-Cox'
        else:
            transformation = None

        return transformation

    @classmethod
    def variance_dists_after_transformation_analysis(cls, show_results: Dict, series: pd.Series):
        """
        :param series:
        :param show_results: show_results attribute from VarianceShowTests.show_distribution_plot
        """
        transform = cls.variance_dists_after_transformation_choice(show_results)

        if transform is None:
            return transform

        if transform == 'Logarithm':
            series_t = LogTransformation.transform(series)
        else:
            series_t = BoxCox().transform(series)

        dist_or, dist_t = KolmogorovSmirnov.best_dist_in_two_parts(series, series_t)

        if dist_or == dist_or:
            if dist_or is None:
                var_dists_after_t = gettext('variance_dists_equal_and_none').format(transform)
            else:
                var_dists_after_t = gettext('variance_dists_equal').format(transform, dist_or)
        else:
            if dist_or is None:
                var_dists_after_t = gettext('variance_dists_diff_p1none').format(transform, dist_t)
            elif dist_t is None:
                var_dists_after_t = gettext('variance_dists_diff_p2none').format(transform, dist_or)
            else:
                var_dists_after_t = gettext('variance_dists_diff').format(transform, dist_or, dist_t)

        return var_dists_after_t


class VarianceShowTests:

    @staticmethod
    def show_distribution_plot(tests: VarianceTesting) -> Tuple[bool, Dict]:
        """
        show_me, show_results = VarianceShowTests.show_distribution_plot(ds.tests.variance)

        :param tests: VarianceTesting object
        """
        is_heteroskedastic = tests.prob_heteroskedastic > 0
        log_improves = tests.performance['base'] > tests.performance['log']
        boxcox_improves = tests.performance['base'] > tests.performance['boxcox']
        exists_groupdiff = len(tests.group_var) > 0

        show_me = is_heteroskedastic or log_improves or boxcox_improves or exists_groupdiff

        show_results = {
            'by_st': is_heteroskedastic,
            'by_log': log_improves,
            'by_boxcox': boxcox_improves,
            'by_groupdiff': exists_groupdiff,
        }

        return show_me, show_results
