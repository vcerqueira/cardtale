import pandas as pd

import plotnine as p9
from scipy.stats import linregress
from numerize import numerize

from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY


class Scatterplot:
    """
    Class for creating scatter plots.

    Methods:
        lagplot(data, x_axis_col, y_axis_col, x_lab, y_lab, title, add_perfect_abline, add_slope_abline):
            Creates a scatter plot with optional perfect and slope ablines.
    """

    @staticmethod
    def lagplot(data: pd.DataFrame,
                x_axis_col: str,
                y_axis_col: str,
                x_lab: str = '',
                y_lab: str = '',
                title: str = '',
                add_perfect_abline: bool = False,
                add_slope_abline: bool = False):
        """
        Creates a scatter plot with optional perfect and slope ablines.

        Args:
            data (pd.DataFrame): Data for the plot.
            x_axis_col (str): Column name for the x-axis.
            y_axis_col (str): Column name for the y-axis.
            x_lab (str, optional): Label for the x-axis. Defaults to ''.
            y_lab (str, optional): Label for the y-axis. Defaults to ''.
            title (str, optional): Title of the plot. Defaults to ''.
            add_perfect_abline (bool, optional): Flag to add a perfect abline. Defaults to False.
            add_slope_abline (bool, optional): Flag to add a slope abline. Defaults to False.

        Returns:
            plotnine.ggplot: The generated scatter plot.
        """


        aes_ = {'x': x_axis_col, 'y': y_axis_col}

        plot = p9.ggplot(data) + \
               p9.aes(**aes_) + \
               p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
               p9.theme(plot_margin=.0125,
                        axis_text_y=p9.element_text(size=10),
                        axis_text_x=p9.element_text(size=10))

        if add_slope_abline:
            lm = linregress(data[x_axis_col], data[y_axis_col])
            plot += \
                p9.geom_abline(intercept=lm.intercept,
                               slope=lm.slope,
                               size=1.2,
                               color=THEME_PALETTE[THEME]['soft'],
                               linetype='dashed')

        if add_perfect_abline:
            plot += \
                p9.geom_abline(intercept=0,
                               slope=1,
                               size=1.2,
                               color=THEME_PALETTE[THEME]['hard'],
                               linetype='dashed')

        plot += p9.geom_point(color=THEME_PALETTE[THEME]['black'])

        plot = \
            plot + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ggtitle(title) + \
            p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst]) + \
            p9.scale_x_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot
