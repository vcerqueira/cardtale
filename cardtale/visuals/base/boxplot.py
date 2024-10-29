import pandas as pd

import plotnine as p9
from numerize import numerize
from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY


class Boxplot:
    """
    Class for creating boxplots.

    Methods:
        univariate_flipped(data, y_axis_col, x_lab, y_lab, title):
            Creates a univariate boxplot with flipped coordinates.
    """

    @staticmethod
    def univariate_flipped(data: pd.DataFrame,
                           y_axis_col: str,
                           x_lab: str = '',
                           y_lab: str = '',
                           title: str = ''):
        """
        Creates a univariate boxplot with flipped coordinates.

        Args:
            data (pd.DataFrame): Data for the plot.
            y_axis_col (str): Column name for the y-axis.
            x_lab (str, optional): Label for the x-axis. Defaults to ''.
            y_lab (str, optional): Label for the y-axis. Defaults to ''.
            title (str, optional): Title of the plot. Defaults to ''.

        Returns:
            plotnine.ggplot: The generated boxplot.
        """

        aes_ = {'x': 1, 'y': y_axis_col}

        plot = p9.ggplot(data, p9.aes(**aes_)) + \
               p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
               p9.theme(plot_margin=0.015,
                        axis_text=p9.element_text(size=12),
                        axis_text_y=p9.element_blank(),
                        legend_title=p9.element_blank(),
                        legend_position=None) + \
               p9.geom_boxplot(fill=THEME_PALETTE[THEME]['hard'],
                               color=THEME_PALETTE[THEME]['black'],
                               show_legend=False) + \
               p9.xlab(x_lab) + \
               p9.ylab(y_lab) + \
               p9.ggtitle(title) + \
               p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst]) + \
               p9.coord_flip()

        return plot
