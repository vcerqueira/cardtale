from cardtale.visuals.plot import Plot
from cardtale.core.data import TimeSeriesData
from cardtale.visuals.base.lollipop import Lollipop
from cardtale.cards.strings import join_l, gettext
from cardtale.visuals.config import PLOT_NAMES


class SeriesACFPlot(Plot):
    """
    Class for creating and analyzing autocorrelation function (ACF) plots.

    Attributes:
        caption (str): Caption for the plot.
        show_me (bool): Flag indicating if the plot should be shown.
        plot_name (str): Name of the plot.
    """

    def __init__(self, tsd: TimeSeriesData, name: str):
        """
        Initializes the SeriesACFPlot class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            name (str): Name of the plot.
        """

        super().__init__(tsd=tsd, multi_plot=False, name=name)

        self.caption = gettext('series_acf_caption')
        self.show_me = True

        self.plot_name = PLOT_NAMES['struc_acf']

    def build(self):
        """
        Creates the ACF plot.
        """

        self.plot = Lollipop.with_point(data=self.tsd.summary.acf.acf_df,
                                        x_axis_col='Lag',
                                        y_axis_col='ACF',
                                        h_threshold=self.tsd.summary.acf.significance_thr)

    def analyse(self):
        """
        Analyzes the ACF plot.

        The analysis includes identifying significant lags and seasonal lags.
        """

        acf_ = self.tsd.summary.acf.acf_analysis

        if len(acf_['significant_ids']) < 1:
            acf_analysis_sign = gettext('series_acf_analysis_wn')
            self.analysis.append(acf_analysis_sign)
        else:
            significant_lags = [f't-{i}' for i in acf_['significant_ids']]
            acf_anl_sign_which = gettext('series_acf_analysis_slags1').format(join_l(significant_lags))

            if len(acf_['under_thr_ids']) > 0 and len(acf_['over_thr_ids']) > 0:
                neg_signf_lags = [f't-{i}' for i in acf_['under_thr_ids']]
                pos_signf_lags = [f't-{i}' for i in acf_['over_thr_ids']]
                acf_anl_sign_which += gettext('series_acf_analysis_slags1a').format(join_l(neg_signf_lags),
                                                                                    join_l(pos_signf_lags))
            elif len(acf_['under_thr_ids']) > 0 and len(acf_['over_thr_ids']) == 0:
                acf_anl_sign_which += gettext('series_acf_analysis_slags1b')
            elif len(acf_['under_thr_ids']) == 0 and len(acf_['over_thr_ids']) > 0:
                acf_anl_sign_which += gettext('series_acf_analysis_slags1c')
            else:
                pass

            self.analysis.append(acf_anl_sign_which)

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

        self.analysis.append(seasonal_lag_analysis)

    def format_caption(self, plot_id: int):
        """
        Formats the caption with the respective number and method.

        Args:
            plot_id (int): Plot id.
        """

        self.img_data['caption'] = self.img_data['caption'].format(plot_id,
                                                                   self.tsd.summary.acf.n_lags)
