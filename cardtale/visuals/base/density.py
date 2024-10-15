import pandas as pd

from plotnine import *
from numerize import numerize

from cardtale.visuals.config import (PISTACHIO_HARD,
                                    BROWN_HARD,
                                    WHITE)


class PlotDensity:

    @staticmethod
    def by_group(data: pd.DataFrame,
                 x_axis_col: str,
                 group_col: str,
                 x_lab: str = '',
                 y_lab: str = '',
                 title: str = ''):

        data_grp = data.groupby(group_col).mean().reset_index()
        data_grp.set_index(group_col, inplace=True)

        plot = ggplot(data) + \
               aes(x=x_axis_col, fill=group_col) + \
               theme_minimal(base_family='Palatino', base_size=12) + \
               theme(plot_margin=.0175,
                     axis_text=element_text(size=12),
                     legend_title=element_blank(),
                     legend_position='top')

        for grp in data_grp[x_axis_col]:
            plot += geom_vline(xintercept=grp,
                               linetype='dashed',
                               color='steelblue',
                               size=1.1,
                               alpha=0.7)

        plot = plot + \
               geom_density(alpha=.2) + \
               xlab(x_lab) + \
               ylab(y_lab) + \
               ggtitle(title)

        return plot

    @staticmethod
    def by_pair(data: pd.DataFrame,
                x_axis_col: str,
                group_col: str,
                numerize_x: bool = True,
                numerize_y: bool = True,
                x_lab: str = '',
                y_lab: str = '',
                title: str = ''):

        COLORS = [PISTACHIO_HARD, BROWN_HARD]

        data_grp = data.groupby(group_col).mean().reset_index()
        data_grp.set_index(group_col, inplace=True)

        plot = ggplot(data) + \
               aes(x=x_axis_col, color=group_col, fill=group_col) + \
               theme_minimal(base_family='Palatino', base_size=12) + \
               theme(plot_margin=.0175,
                     axis_text=element_text(size=12),
                     strip_text=element_text(size=12),
                     #panel_background=element_rect(fill=WHITE),
                     #plot_background=element_rect(fill=WHITE),
                     #strip_background=element_rect(fill=WHITE),
                     #legend_background=element_rect(fill=WHITE),
                     legend_title=element_blank(),
                     legend_position='top')

        for i, grp in enumerate(data_grp[x_axis_col]):
            plot += geom_vline(xintercept=grp,
                               linetype='dashed',
                               color=COLORS[i],
                               size=1.1,
                               alpha=0.7)

        plot = plot + \
               geom_density(aes(y=after_stat('density')), alpha=.3) + \
               xlab(x_lab) + \
               ylab(y_lab) + \
               ggtitle(title) + \
               scale_fill_manual(values=COLORS) + \
               scale_color_manual(values=COLORS)

        if numerize_x:
            plot = \
                plot + \
                scale_x_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        if numerize_y:
            plot = \
                plot + \
                scale_y_continuous(labels=lambda lst: [f'{x:.1e}' for x in lst])

        return plot
