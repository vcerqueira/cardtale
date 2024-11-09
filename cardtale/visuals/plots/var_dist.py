from typing import List, Optional

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.violin_partial import PartialViolinPlot
from cardtale.cards.strings import join_l, gettext
from cardtale.analytics.testing.card.variance import VarianceTestsParser
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.core.utils.splits import DataSplit
from cardtale.core.config.analysis import GOLDFELD_Q_PARTITION
from cardtale.visuals.config import PLOT_NAMES
from cardtale.core.config.analysis import ALPHA


class VarianceDistPlots(Plot):
    """
    Class for creating and analyzing variance distribution plots.

    Attributes:
        caption (str): Caption for the plot.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for variance analysis.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: List[str]):
        """
        Initializes the VarianceDistPlots class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for variance analysis.
            name (List[str]): Name(s) of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.caption = gettext('variance_partition_caption')

        self.plot_name = PLOT_NAMES['var_dist']

        self.tests = tests

        # self.s = self.tsd.get_target_series(df=self.tsd.df,
        #                                     time_col=self.tsd.time_col,
        #                                     target_col=self.tsd.target_col)

    def build(self, *args, **kwargs):
        """
        Creates the variance distribution plots.
        """
        levels = ['Last 33% \n Residuals', 'First 33% \n Residuals']

        gf_parts = DataSplit.goldfeldquant_partition(self.tests.variance.residuals,
                                                     GOLDFELD_Q_PARTITION,
                                                     partition_names=levels)

        gf_parts['Part'] = DataSplit.df_var_to_categorical(gf_parts, 'Part', levels)

        plot_part_residuals = \
            PartialViolinPlot.partial_violin(data=gf_parts,
                                             x_axis_col='Part',
                                             y_axis_col='Residuals',
                                             group_col='Id',
                                             y_lab='Residuals value',
                                             flip_coords=True)

        self.plot = plot_part_residuals

    def analyse(self, *args, **kwargs):
        """
        Analyzes the variance distribution plots.

        The analysis includes checking for significant differences in variance and summarizing the results.
        """

        self.show_me, show_results = VarianceTestsParser.show_distribution_plot(self.tests.variance)

        if not self.show_me:
            return

        plt_deq1 = self.deq_group_variances()
        plt_deq2 = self.deq_heteroskedasticity_tests()
        plt_deq3 = self.deq_accuracy_var_stabilizers()

        self.analysis = [plt_deq1, plt_deq2, plt_deq3]
        self.analysis = [x for x in self.analysis if x is not None]

    def deq_group_variances(self) -> Optional[str]:
        """
        DEQ: Are there significant differences in variance of period groups?

        Approach:
            - Levene's test
        """

        if len(self.tests.variance.groups_with_diff_var) > 0:
            expr = gettext('variance_partition_analysis_seas')
            expr_fmt = expr.format(join_l(self.tests.variance.groups_with_diff_var))
        else:
            expr_fmt = gettext('variance_partition_analysis_seas_none')

        return expr_fmt

    def deq_heteroskedasticity_tests(self) -> Optional[str]:
        """
        DEQ: Is the time series heteroskedastic?

        Approach:
            - Statistical tests
        """

        tests = self.tests.variance.tests

        prob_heterosk = tests.mean()

        test_names = tests.index.tolist()
        rej_nms = tests[tests < ALPHA].index.tolist()
        n_rej_nms = tests[tests > ALPHA].index.tolist()

        if prob_heterosk > 0:
            if prob_heterosk == 1:
                expr = gettext('variance_partition_analysis_heterosk_prob_all')
                expr_fmt = expr.format(join_l(test_names))
            else:
                expr = gettext('variance_partition_analysis_heterosk_prob_some')
                expr_fmt = expr.format(join_l(rej_nms), join_l(n_rej_nms))
        else:
            expr = gettext('variance_partition_analysis_heterosk_prob_none')
            expr_fmt = expr.format(join_l(test_names))

        return expr_fmt

    def deq_accuracy_var_stabilizers(self) -> Optional[str]:
        """
        DEQ: Do variance stabilization methods improve forecasting performance?

        Approach:
            - Log transformation
            - Box-Cox transformation
            - CV
        """

        # <strong>Preliminary experiments: </strong> Three variance stabilization preprocessing techniques were tested to improve the forecast accuracy of an auto-regressive LightGBM (with {}% SMAPE using lag-based features). Using the original time series led to a {}% SMAPE. The scores using the differenced and log differenced time series are {}% and {}%, respectively.

        tests = self.tests.variance

        log_improves = tests.performance['base'] > tests.performance['log']
        logd_improves = tests.performance['base'] > self.tests.trend.performance['log_differences']
        bc_improves = tests.performance['base'] > tests.performance['boxcox']

        if log_improves or bc_improves:
            if log_improves and bc_improves:
                expr_fmt = gettext('variance_partition_analysis_perf_both')
            else:
                expr = gettext('variance_partition_analysis_perf_one')
                if log_improves:
                    expr_fmt = expr.format('logarithm', 'Box-Cox method')
                else:
                    expr_fmt = expr.format('Box-Cox method', 'logarithm')
        else:
            expr_fmt = gettext('variance_partition_analysis_perf_none')

        return expr_fmt
