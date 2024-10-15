import pandas as pd
from numerize import numerize
from plotnine import *

from cardtale.visuals.base.summary import SummaryStatPlot
from cardtale.visuals.config import (PISTACHIO_HARD,
                                    PISTACHIO_SOFT,
                                    WHITE)


class SeasonalPlot:
    COLOR_LIST = [
        '#F8766D', '#D39200', '#93AA00', '#00BA38', '#00C19F',
        '#00B9E3', '#619CFF', '#DB72FB', '#FF61C3'
    ]

    @classmethod
    def lines(cls,
              data: pd.DataFrame,
              x_axis_col: str,
              y_axis_col: str,
              group_col: str,
              numerize_y: bool = True,
              x_lab: str = '',
              y_lab: str = '',
              title: str = '',
              add_labels: bool = True,
              add_smooth: bool = False):

        plot = \
            ggplot(data) + \
            aes(x=x_axis_col,
                y=y_axis_col,
                group=group_col,
                color=group_col) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.0125,
                  axis_text=element_text(size=10),
                  #panel_background=element_rect(fill=WHITE),
                  #plot_background=element_rect(fill=WHITE),
                  #strip_background=element_rect(fill=WHITE),
                  #legend_background=element_rect(fill=WHITE),
                  legend_title=element_blank()) + \
            scale_color_gradientn(colors=cls.COLOR_LIST)

        if add_smooth:
            plot += geom_smooth(group=1,
                                size=3,
                                color='lightgray',
                                alpha=0.4)

        plot += geom_line()

        if add_labels:
            data_labs = data.groupby(group_col).apply(lambda x: x.iloc[[0, -1], :])

            plot += geom_text(data=data_labs,
                              mapping=aes(label=group_col))

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

    @staticmethod
    def sub_series(data: pd.DataFrame,
                   x_axis_col: str,
                   y_axis_col: str,
                   group_col: str,
                   numerize_y: bool = True,
                   x_lab: str = '',
                   y_lab: str = '',
                   title: str = ''):

        stat_by_group, _ = SummaryStatPlot.summary_by_group(data, y_axis_col, group_col, 'mean')
        stat_by_group = stat_by_group.reset_index()

        plot = \
            ggplot(data) + \
            aes(x=x_axis_col,
                y=y_axis_col) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.0125,
                  axis_text_x=element_text(size=8, angle=90),
                  #panel_background=element_rect(fill=WHITE),
                  #plot_background=element_rect(fill=WHITE),
                  #strip_background=element_rect(fill=WHITE),
                  #legend_background=element_rect(fill=WHITE),
                  legend_title=element_blank(),
                  strip_background_x=element_text(color=PISTACHIO_SOFT),
                  strip_text_x=element_text(size=11))

        plot += geom_line()
        plot += facet_grid(f'. ~{group_col}')
        plot += geom_hline(data=stat_by_group,
                           mapping=aes(yintercept=y_axis_col),
                           colour=PISTACHIO_HARD,
                           size=1)

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
