import pandas as pd
import plotnine as p9
from plotnine.geoms.geom_hline import geom_hline

from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY


class Lollipop:
    """
    Class for creating lollipop plots.

    Methods:
        with_point(data, x_axis_col, y_axis_col, h_threshold, x_lab, y_lab, title):
            Creates a lollipop plot with optional horizontal threshold.
    """

    @staticmethod
    def with_point(data: pd.DataFrame,
                   x_axis_col: str,
                   y_axis_col: str,
                   h_threshold: float = 0,
                   x_lab: str = '',
                   y_lab: str = '',
                   title: str = ''):
        """
        Creates a lollipop plot with optional horizontal threshold.

        Args:
            data (pd.DataFrame): Data for the plot.
            x_axis_col (str): Column name for the x-axis.
            y_axis_col (str): Column name for the y-axis.
            h_threshold (float, optional): Horizontal threshold. Defaults to 0.
            x_lab (str, optional): Label for the x-axis. Defaults to ''.
            y_lab (str, optional): Label for the y-axis. Defaults to ''.
            title (str, optional): Title of the plot. Defaults to ''.

        Returns:
            plotnine.ggplot: The generated lollipop plot.
        """

        aes_ = {'x': x_axis_col, 'y': y_axis_col}
        aes_s = {'x': x_axis_col, 'xend': x_axis_col, 'y': 0, 'yend': y_axis_col}

        plot = p9.ggplot(data=data, mapping=p9.aes(**aes_))

        if h_threshold != 0:
            plot += geom_hline(yintercept=h_threshold,
                               linetype='dashed',
                               color=THEME_PALETTE[THEME]['mid'],
                               size=.8)
            plot += geom_hline(yintercept=-h_threshold,
                               linetype='dashed',
                               color=THEME_PALETTE[THEME]['mid'],
                               size=.8)

        plot += geom_hline(yintercept=0, linetype='solid', color='black', size=1)

        plot = \
            plot + p9.geom_segment(p9.aes(**aes_s),
                                   size=1.5,
                                   color=THEME_PALETTE[THEME]['soft']) + \
            p9.geom_point(size=4, color=THEME_PALETTE[THEME]['hard']) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text_y=p9.element_text(size=12),
                     axis_text_x=p9.element_text(size=10),
                     legend_title=p9.element_blank(),
                     legend_position='none') + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ylim(-1, 1) + \
            p9.ggtitle(title)

        return plot
