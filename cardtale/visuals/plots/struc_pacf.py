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

    def build(self):
        """
        Creates the PACF plot.
        """

        self.plot = Lollipop.with_point(data=self.tsd.summary.pacf.acf_df,
                                        x_axis_col='Lag',
                                        y_axis_col='ACF',
                                        h_threshold=self.tsd.summary.pacf.significance_thr)

    def analyse(self):
        """
        Analyzes the PACF plot.

        The analysis includes identifying significant lags and seasonal lags.
        """

        acf_ = self.tsd.summary.pacf.acf_analysis

        if len(acf_['significant_ids']) < 1:
            acf_analysis_sign = gettext('series_acf_analysis_wn')
            self.analysis.append(acf_analysis_sign)
        else:
            significant_lags = [f't-{i}' for i in acf_['significant_ids']]
            acf_analysis_sign = gettext('series_acf_analysis_slags1').format(join_l(significant_lags))

        acf_analysis_sign = re.sub(ACF_NAME, PACF_NAME, acf_analysis_sign)
        self.analysis.append(acf_analysis_sign)

        seas_signf_lags = acf_['seasonal_lags_sig']
        seas_signf_lags_nm = [f't-{i}' for i in seas_signf_lags.index]

        if all(acf_['seasonal_lags_sig']):
            seasonal_lag_analysis = gettext('series_acf_analysis_seas_all').format(join_l(seas_signf_lags_nm))
        else:
            if all(~acf_['seasonal_lags_sig']):
                seasonal_lag_analysis = gettext('series_acf_analysis_seas_none').format(join_l(seas_signf_lags_nm))
            else:
                seas_signf_lags_ = seas_signf_lags[seas_signf_lags]
                seas_signf_lags_nm_ = [f't-{i}' for i in seas_signf_lags_.index]
                seasonal_lag_analysis = gettext('series_acf_analysis_seas_some').format(join_l(seas_signf_lags_nm_))

        seasonal_lag_analysis = re.sub(ACF_NAME, PACF_NAME, seasonal_lag_analysis)
        self.analysis.append(seasonal_lag_analysis)

    def format_caption(self, plot_id: int):
        """
        Formats the caption with the respective number and method.

        Args:
            plot_id (int): Plot id.
        """

        self.img_data['caption'] = self.img_data['caption'].format(plot_id,
                                                                   self.tsd.summary.acf.n_lags)
