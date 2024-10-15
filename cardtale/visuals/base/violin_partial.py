import pandas as pd
from plotnine import *
from numerize import numerize

from cardtale.visuals.config import (BROWN_HARD,
                                    PISTACHIO_HARD,
                                    WHITE)


class PartialViolinPlot:

    @staticmethod
    def alt_sign(x):
        "Alternate +1/-1 if x is even/odd"
        return (-1) ** x

    @classmethod
    def partial_violin(cls,
                       data: pd.DataFrame,
                       x_axis_col: str,
                       y_axis_col: str,
                       group_col: str,
                       numerize_y: bool = True,
                       x_lab: str = '',
                       y_lab: str = '',
                       title: str = ''):
        x = stage(x_axis_col, after_scale='x+shift*cls.alt_sign(x)')

        shift = 0.15
        lsize = 0.8
        fill_alpha = 0.7

        m1 = aes(x=stage(x_axis_col, after_scale='x+shift*cls.alt_sign(x)'))
        m2 = aes(x=stage(x_axis_col, after_scale='x-shift*cls.alt_sign(x)'),
                 group=group_col)

        plot = \
            ggplot(data=data,
                   mapping=aes(x=x_axis_col, y=y_axis_col, fill=x_axis_col)) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.0125,
                  axis_text=element_text(size=12),
                  #panel_background=element_rect(fill=WHITE),
                  #plot_background=element_rect(fill=WHITE),
                  #strip_background=element_rect(fill=WHITE),
                  #legend_background=element_rect(fill=WHITE),
                  legend_title=element_blank(),
                  legend_position=None) + \
            geom_violin(m1,
                        style='left-right',
                        alpha=fill_alpha,
                        size=lsize,
                        show_legend=False) + \
            geom_point(m2,
                       color='none',
                       alpha=fill_alpha,
                       size=4,
                       show_legend=False) + \
            geom_boxplot(width=.15,
                         alpha=fill_alpha,
                         size=.5,
                         show_legend=False) + \
            scale_fill_manual(values=[PISTACHIO_HARD, BROWN_HARD])

        plot = \
            plot + \
            xlab(x_lab) + \
            ylab(y_lab) + \
            ggtitle(title)

        if numerize_y:
            plot = \
                plot + \
                scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot
