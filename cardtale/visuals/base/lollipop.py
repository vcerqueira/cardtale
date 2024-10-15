import pandas as pd
from plotnine import *

from cardtale.visuals.config import (PISTACHIO_MID,
                                    PISTACHIO_HARD,
                                    PISTACHIO_SOFT,
                                    WHITE)


class Lollipop:

    @staticmethod
    def with_point(data: pd.DataFrame,
                   x_axis_col: str,
                   y_axis_col: str,
                   h_threshold: float = 0,
                   x_lab: str = '',
                   y_lab: str = '',
                   title: str = ''):
        plot = ggplot(data, aes(x=x_axis_col, y=y_axis_col))

        if h_threshold != 0:
            plot += geom_hline(yintercept=h_threshold,
                               linetype='dashed',
                               color=PISTACHIO_MID,
                               size=.8)
            plot += geom_hline(yintercept=-h_threshold,
                               linetype='dashed',
                               color=PISTACHIO_MID,
                               size=.8)

        plot += geom_hline(yintercept=0, linetype='solid', color='black', size=1)

        plot = \
            plot + geom_segment(
                aes(x=x_axis_col,
                    xend=x_axis_col,
                    y=0,
                    yend=y_axis_col),
                size=1.5,
                color=PISTACHIO_SOFT
            ) + \
            geom_point(
                size=4,
                color=PISTACHIO_HARD,
            ) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.0125,
                  axis_text_y=element_text(size=12),
                  axis_text_x=element_text(size=10),
                  #panel_background=element_rect(fill=WHITE),
                  #plot_background=element_rect(fill=WHITE),
                  #strip_background=element_rect(fill=WHITE),
                  #legend_background=element_rect(fill=WHITE),
                  legend_title=element_blank(),
                  legend_position='none')

        plot = plot + \
               xlab(x_lab) + \
               ylab(y_lab) + \
               ylim(-1, 1) + \
               ggtitle(title)

        return plot
