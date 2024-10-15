import pandas as pd
from plotnine import *

from scipy.stats import linregress
from numerize import numerize

from cardtale.visuals.config import (PISTACHIO_HARD,
                                    PISTACHIO_BLACK,
                                    WHITE)


class Scatterplot:

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

        :param data:
        :param x_axis_col:
        :param y_axis_col:
        :param x_lab:
        :param y_lab:
        :param title:
        :param add_perfect_abline:
        :param add_slope_abline:
        :return:
        """

        plot = ggplot(data) + \
               aes(x=x_axis_col, y=y_axis_col) + \
               theme_minimal(base_family='Palatino', base_size=12) + \
               theme(plot_margin=.0125,
                     axis_text_y=element_text(size=10),
                     #panel_background=element_rect(fill=WHITE),
                     #plot_background=element_rect(fill=WHITE),
                     #strip_background=element_rect(fill=WHITE),
                     #legend_background=element_rect(fill=WHITE),
                     axis_text_x=element_text(size=10))

        if add_slope_abline:
            lm = linregress(data[x_axis_col], data[y_axis_col])
            plot += \
                geom_abline(intercept=lm.intercept,
                            slope=lm.slope,
                            size=1.2,
                            color='red',
                            linetype='dashed')

        if add_perfect_abline:
            plot += \
                geom_abline(intercept=0,
                            slope=1,
                            size=1.2,
                            color=PISTACHIO_HARD,
                            linetype='dashed')

        plot += geom_point(color=PISTACHIO_BLACK)

        plot = \
            plot + \
            xlab(x_lab) + \
            ylab(y_lab) + \
            ggtitle(title)

        plot = \
            plot + \
            scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst]) + \
            scale_x_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot
