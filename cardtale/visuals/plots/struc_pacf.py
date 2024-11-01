from typing import Optional
import re

from cardtale.visuals.plot import Plot
from cardtale.visuals.base.lollipop import Lollipop
from cardtale.cards.strings import join_l, gettext
from cardtale.core.data import TimeSeriesData
from cardtale.visuals.config import PLOT_NAMES

ACF_NAME, PACF_NAME = 'autocorrelation', 'partial autocorrelation'


class SeriesPACFPlot(Plot):
    """
    Class for creating and analyzing partial autocorrelation function (PACF) plots.

    Attributes:
        caption (str): Caption for the plot.
        show_me (bool): Flag indicating if the plot should be shown.
        plot_name (str): Name of the plot.
    """

    HEIGHT = 4

    def __init__(self, tsd: TimeSeriesData, name: str):
        """
        Initializes the SeriesPACFPlot class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            name (str): Name of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.caption = gettext('series_pacf_caption')
        self.show_me = True

        self.plot_name = PLOT_NAMES['struc_pacf']

    def build(self, *args, **kwargs):
        """
        Creates the PACF plot.
        """

        self.plot = Lollipop.with_point(data=self.tsd.summary.pacf.acf_df,
                                        x_axis_col='Lag',
                                        y_axis_col='ACF',
                                        h_threshold=self.tsd.summary.pacf.significance_thr)

    def analyse(self, *args, **kwargs):
        """
        Analyzes the PACF plot.

        The analysis includes identifying significant lags and seasonal lags.
        """

        plt_deq1 = self.deq_pacf_nonseasonal()
        plt_deq2 = self.deq_pacf_seasonal()

        self.analysis = [plt_deq1, plt_deq2]
        self.analysis = [x for x in self.analysis if x is not None]

    def format_caption(self, plot_id: int):
        """
        Formats the caption with the respective number and method.

        Args:
            plot_id (int): Plot id.
        """

        self.img_data['caption'] = \
            self.img_data['caption'].format(plot_id,
                                            self.tsd.summary.acf.n_lags)

    def deq_pacf_nonseasonal(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Are there any significant non-seasonal lags in the PACF?

        Approach:
            - PACF analysis
        """

        acf_scores = self.tsd.summary.pacf.acf_analysis
        n_significant = len(acf_scores['significant_ids'])

        if n_significant < 1:
            expr_fmt = gettext('series_acf_analysis_wn')
        else:
            significant_lags = [f't-{i}' for i in acf_scores['significant_ids']]
            expr = gettext('series_acf_analysis_slags1')
            expr_fmt = expr.format(join_l(significant_lags))
            expr_fmt = re.sub(ACF_NAME, PACF_NAME, expr_fmt)

        return expr_fmt

    def deq_pacf_seasonal(self) -> Optional[str]:
        """
        DEQ (Data Exploratory Question): Are there any significant seasonal lags in the PACF?

        Approach:
            - PACF analysis
        """

        acf_scores = self.tsd.summary.pacf.acf_analysis

        seas_signf_lags = acf_scores['seasonal_lags_sig']
        seas_signf_lags_nm = [f't-{i}' for i in seas_signf_lags.index]

        if all(seas_signf_lags):
            expr = gettext('series_acf_analysis_seas_all')
            expr_fmt = expr.format(join_l(seas_signf_lags_nm))
        else:
            if all(~seas_signf_lags):
                expr = gettext('series_acf_analysis_seas_none')
                expr_fmt = expr.format(join_l(seas_signf_lags_nm))
            else:
                seas_signf_lags_ = seas_signf_lags[seas_signf_lags]
                seas_signf_lags_nm_ = [f't-{i}' for i in seas_signf_lags_.index]

                expr = gettext('series_acf_analysis_seas_some')
                expr_fmt = expr.format(join_l(seas_signf_lags_nm_))

        expr_fmt = re.sub(ACF_NAME, PACF_NAME, expr_fmt)

        return expr_fmt
