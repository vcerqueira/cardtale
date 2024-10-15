import pandas as pd

from plotnine import *
from numerize import numerize
from cardtale.visuals.config import (PISTACHIO_HARD,
                                    PISTACHIO_BLACK,
                                    WHITE)


class Boxplot:

    @staticmethod
    def univariate(data: pd.DataFrame,
                   x_axis_col: str,
                   y_axis_col: str,
                   x_lab: str = '',
                   y_lab: str = '',
                   title: str = ''):
        """
        :param y_axis_col:
        :param data:
        :param x_axis_col:
        :param n_bins:
        :param x_lab:
        :param y_lab:
        :param title:
        :return:
        """

        plot = ggplot(data, aes(x=x_axis_col, y=y_axis_col)) + \
               theme_minimal(base_family='Palatino', base_size=12) + \
               theme(plot_margin=0.015,
                     axis_text=element_text(size=12),
                     axis_text_x=element_blank(),
                     legend_title=element_blank(),
                     legend_position=None) + \
               geom_boxplot(fill='#66CDAA',
                            width=0.3,
                            show_legend=False)

        plot = \
            plot + \
            xlab(x_lab) + \
            ylab(y_lab) + \
            ggtitle(title)

        return plot

    @staticmethod
    def univariate_flipped(data: pd.DataFrame,
                           y_axis_col: str,
                           x_lab: str = '',
                           y_lab: str = '',
                           title: str = ''):
        plot = ggplot(data, aes(x=1, y=y_axis_col)) + \
               theme_minimal(base_family='Palatino', base_size=12) + \
               theme(plot_margin=0.015,
                     axis_text=element_text(size=12),
                     axis_text_y=element_blank(),
                     #panel_background=element_rect(fill=WHITE),
                     #plot_background=element_rect(fill=WHITE),
                     #strip_background=element_rect(fill=WHITE),
                     #legend_background=element_rect(fill=WHITE),
                     legend_title=element_blank(),
                     legend_position=None) + \
               geom_boxplot(fill=PISTACHIO_HARD,
                            color=PISTACHIO_BLACK,
                            show_legend=False)

        plot = \
            plot + \
            xlab(x_lab) + \
            ylab(y_lab) + \
            ggtitle(title)

        plot = \
            plot + \
            scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        plot += coord_flip()

        return plot
