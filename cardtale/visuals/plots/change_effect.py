from typing import List, Optional

import numpy as np
import pandas as pd

from cardtale.visuals.plot import Plot
from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.visuals.base.density import PlotDensity
from cardtale.cards.strings import gettext
from cardtale.core.config.analysis import ALPHA
from cardtale.visuals.config import PLOT_NAMES


class ChangeEffectPlots(Plot):
    """
    Class for creating and analyzing change distribution plots.
    Using a partial violin plot and a density plot.

    Attributes:
        caption (str): Caption for the plot.
        plot_name (str): Name of the plot.
        tests (TestingComponents): Testing components for change detection.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents, name: str):
        """
        Initializes the ChangeDistPlots class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            tests (TestingComponents): Testing components for change detection.
            name (List[str]): Name(s) of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.caption = gettext('change_beforeafter_caption')
        self.plot_name = PLOT_NAMES['change_effect']

        self.tests = tests

    def build(self, *args, **kwargs):
        """
        Creates the change distribution plot.
        """

        if self.show_me:
            cp, _ = self.tests.change.get_change_points()

            data_parts = self.tests.change.resid_df

            parts_dens = PlotDensity.by_pair(data_parts,
                                             x_axis_col='Residuals',
                                             group_col='Part',
                                             x_lab='Residuals')

            self.plot = parts_dens

    def analyse(self, *args, **kwargs):
        """
        Analyzes the change in distribution.

        The analysis includes checking for significant changes and identifying
        the best distributions before and after the change point.
        """
        cp, _ = self.tests.change.get_change_points()

        if len(cp) < 1:
            self.show_me = False
            return

        self.show_me = True

        # there's at least one change point
        plt_deq1 = self.deq_chow_test()
        plt_deq2 = self.deq_accuracy_step_intervention()

        self.analysis = [plt_deq1, plt_deq2]
        self.analysis = [x for x in self.analysis if x is not None]

    def deq_chow_test(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Did the distribution change at the first change point?

        Approach:
            - PELT testing
            - Chow test on residuals of ARIMA model
        """

        chow_rejects = self.tests.change.chow_p_value < ALPHA

        expr = gettext('change_effect_chow')

        if chow_rejects:
            conc_ = 'indicating a structural change in the underlying process'
            expr_fmt = expr.format(test_result='rejects',
                                   param_conclusion='are significantly different',
                                   process_conclusion=conc_)
        else:
            conc_ = 'suggesting the underlying process structure remained similar despite the level shift'
            expr_fmt = expr.format(test_result='fails to reject',
                                   order=self.tests.change.arima_ord,
                                   param_conclusion='remain stable',
                                   process_conclusion=conc_)

        return expr_fmt

    def deq_accuracy_step_intervention(self):
        """
        DEQ (Data Exploratory Question): Does a step intervention improve the model accuracy?

        Approach:
            - PELT testing
            - Intervention using step function
        """

        perf = pd.Series(self.tests.change.performance).round(2)

        if np.abs(perf['base'] - perf['step']) < 0.001:
            data = {
                'intervention_effect': 'did not affect',
                'comparison': 'remained the same'
            }
        elif perf['base'] > perf['step']:
            data = {
                'intervention_effect': 'improved',
                'comparison': 'decreased to'
            }
        else:  # base < step
            data = {
                'intervention_effect': 'reduced',
                'comparison': 'increased to'
            }

        expr = gettext('change_effect_accuracy')
        expr_fmt = expr.format(intervention_effect=data['intervention_effect'],
                               base=perf['base'],
                               comparison=data['comparison'],
                               step=perf['step'])

        return expr_fmt
