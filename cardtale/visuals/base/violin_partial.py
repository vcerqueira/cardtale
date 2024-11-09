import pandas as pd
import plotnine as p9
from numerize import numerize

from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY


class PartialViolinPlot:
    """
    Class for creating partial violin plots.

    Attributes:
        SHIFT (float): Shift value for the plot.
        LSIZE (float): Line size for the plot.
        FILL_ALHPA (float): Fill alpha for the plot.
    """

    SHIFT = 0.15
    LSIZE = 0.8
    FILL_ALHPA = 0.7

    @staticmethod
    def alt_sign(x):
        """
        Alternate +1/-1 if x is even/odd.

        Args:
            x (int): Input integer.

        Returns:
            int: +1 if x is even, -1 if x is odd.
        """

        return (-1) ** x

    @classmethod
    def partial_violin(cls,
                       data: pd.DataFrame,
                       x_axis_col: str,
                       y_axis_col: str,
                       group_col: str,
                       x_lab: str = '',
                       y_lab: str = '',
                       title: str = '',
                       flip_coords: bool = False):
        """
        Creates a partial violin plot.

        Args:
            data (pd.DataFrame): Data for the plot.
            x_axis_col (str): Column name for the x-axis.
            y_axis_col (str): Column name for the y-axis.
            group_col (str): Column name for grouping.
            x_lab (str, optional): Label for the x-axis. Defaults to ''.
            y_lab (str, optional): Label for the y-axis. Defaults to ''.
            title (str, optional): Title of the plot. Defaults to ''.
            flip_coords (bool): Whether to flip_coords

        Returns:
            plotnine.ggplot: The generated partial violin plot.
        """

        x = p9.stage(x_axis_col, after_scale='x+cls.SHIFT*cls.alt_sign(x)')

        aes_ = {'x': x_axis_col, 'y': y_axis_col, 'fill': x_axis_col}
        aes_m1 = {'x': p9.stage(x_axis_col, after_scale='x+cls.SHIFT*cls.alt_sign(x)')}
        aes_m2 = {'x': p9.stage(x_axis_col, after_scale='x-cls.SHIFT*cls.alt_sign(x)'), 'group': group_col}

        plot = \
            p9.ggplot(data=data, mapping=p9.aes(**aes_)) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text=p9.element_text(size=12),
                     legend_title=p9.element_blank(),
                     legend_position=None) + \
            p9.geom_violin(p9.aes(**aes_m1),
                           style='left-right',
                           alpha=cls.FILL_ALHPA,
                           size=cls.LSIZE,
                           show_legend=False) + \
            p9.geom_point(p9.aes(**aes_m2),
                          color='none',
                          alpha=cls.FILL_ALHPA,
                          size=4,
                          show_legend=False) + \
            p9.geom_boxplot(width=.15,
                            alpha=cls.FILL_ALHPA,
                            size=.5,
                            show_legend=False) + \
            p9.scale_fill_manual(values=[THEME_PALETTE[THEME]['hard'],
                                         THEME_PALETTE[THEME]['hard_alt']]) + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ggtitle(title) + \
            p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        if flip_coords:
            plot += p9.coord_flip()

        return plot

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
               p9.theme(plot_margin=0.05,
                        axis_text=p9.element_text(size=12),
                        axis_text_y=p9.element_blank(),
                        legend_title=p9.element_blank(),
                        legend_position=None) + \
               p9.geom_violin(fill=THEME_PALETTE[THEME]['hard'],
                              color=THEME_PALETTE[THEME]['black'],
                              show_legend=False) + \
               p9.xlab(x_lab) + \
               p9.ylab(y_lab) + \
               p9.ggtitle(title) + \
               p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst]) + \
               p9.coord_flip()

        return plot
