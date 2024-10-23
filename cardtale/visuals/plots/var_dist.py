from typing import List

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.violin_partial import PartialViolinPlot
from cardtale.cards.strings import join_l, gettext
from cardtale.analytics.testing.card.variance import VarianceShowTests, VarianceTesting
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.core.utils.splits import DataSplit
from cardtale.core.config.analysis import GOLDFELD_Q_PARTITION
from cardtale.visuals.config import PLOT_NAMES


class VarianceDistPlots(Plot):

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: List[str]):
        super().__init__(tsd=tsd, multi_plot=True, name=name)

        self.caption = gettext('variance_partition_caption')

        self.plot_name = PLOT_NAMES['var_dist']

        self.tests = tests

        self.s = self.tsd.get_target_series(df=self.tsd.df,
                                            time_col=self.tsd.time_col,
                                            target_col=self.tsd.target_col)

    def build(self):

        gf_parts = DataSplit.goldfeldquant_partition(self.tests.variance.residuals,
                                                     GOLDFELD_Q_PARTITION,
                                                     partition_names=['First 33% \n Residuals',
                                                                      'Last 33% \n Residuals'])
        gf_parts_series = \
            DataSplit.goldfeldquant_partition(self.s.reset_index(drop=True),
                                              GOLDFELD_Q_PARTITION,
                                              partition_names=['First 33% \n Series Values',
                                                               'Last 33% \n Series Values'])

        plot_part_residuals = \
            PartialViolinPlot.partial_violin(data=gf_parts,
                                             x_axis_col='Part',
                                             y_axis_col='Residuals',
                                             group_col='Id',
                                             y_lab='Residuals value')

        plot_part_series = \
            PartialViolinPlot.partial_violin(data=gf_parts_series,
                                             x_axis_col='Part',
                                             y_axis_col='Residuals',
                                             group_col='Id',
                                             y_lab='Series value')

        self.plot = {'lhs': plot_part_residuals, 'rhs': plot_part_series}

    def analyse(self):

        self.show_me, show_results = VarianceShowTests.show_distribution_plot(self.tests.variance)

        if not self.show_me:
            return

        if len(self.tests.variance.group_var) > 0:
            gd_from_seas = gettext('variance_partition_analysis_seas')
            gd_from_seas = gd_from_seas.format(join_l(self.tests.variance.group_var))
        else:
            gd_from_seas = gettext('variance_partition_analysis_seas_none')

        self.analysis.append(gd_from_seas)

        self.analysis.append(VarianceTesting.variance_st_tests_parser(self.tests.variance.tests))

        self.analysis.append(VarianceTesting.variance_perf_parser(show_results))

        transform_analysis = \
            VarianceTesting.variance_dists_after_transformation_analysis(show_results, self.s)

        if transform_analysis is not None:
            self.analysis.append(transform_analysis)
