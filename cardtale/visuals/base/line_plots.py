from typing import List, Optional, Dict

import pandas as pd

# from kats.consts import TimeSeriesChangePoint

from plotnine import *
from plotnine.geoms.geom_hline import geom_hline
from numerize import numerize

from cardtale.visuals.config import (PISTACHIO_HARD,
                                      PISTACHIO_SOFT,
                                      PISTACHIO_BLACK,
                                      PISTACHIO_MID,
                                      PISTACHIO_FILL,
                                      BROWN_HARD,
                                      WHITE)

OptHLines = Optional[List[geom_hline]]


class LinePlot:

    @staticmethod
    def univariate(data: pd.DataFrame,
                   x_axis_col: str,
                   y_axis_col: str,
                   line_color: str = PISTACHIO_HARD,
                   hline_color: str = PISTACHIO_MID,
                   x_lab: str = '',
                   y_lab: str = '',
                   title: str = '',
                   numerize_y: bool = True,
                   hlines: OptHLines = None,
                   add_smooth: bool = False,
                   ribbons: Optional[Dict[str, str]] = None):

        plot = \
            ggplot(data) + \
            aes(x=x_axis_col, y=y_axis_col, group=1) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.0125,
                  # panel_background=element_rect(fill=WHITE),
                  # plot_background=element_rect(fill=WHITE),
                  # strip_background=element_rect(fill=WHITE),
                  # legend_background=element_rect(fill=WHITE),
                  axis_text=element_text(size=12),
                  legend_title=element_blank(),
                  legend_position=None)

        if add_smooth:
            plot += geom_smooth(color=PISTACHIO_SOFT, size=5)

        plot += geom_line(color=line_color, size=1)

        if hlines is not None:
            for y_inter in hlines:
                plot += geom_hline(yintercept=y_inter,
                                   linetype='dashed',
                                   color=hline_color,
                                   size=1.1)

        if ribbons is not None:
            plot += geom_ribbon(aes(ymin=ribbons['Low'],
                                    ymax=ribbons['High']),
                                alpha=0.2)

        plot = \
            plot + \
            xlab(x_lab) + \
            ylab(y_lab) + \
            ggtitle(title)

        if numerize_y:
            plot = \
                plot + \
                scale_y_continuous(labels=lambda lst: [numerize.numerize(x)
                                                       for x in lst])

        return plot

    @staticmethod
    def univariate_with_h_segments(data: pd.DataFrame,
                                   segments_data: pd.DataFrame,
                                   x_axis_col: str,
                                   y_axis_col: str,
                                   line_color: str = PISTACHIO_MID,
                                   segments_color: str = BROWN_HARD,
                                   x_lab: str = '',
                                   y_lab: str = '',
                                   title: str = '',
                                   numerize_y: bool = True):
        """

        plot = \
            ggplot(series_df) + \
            aes(x='Index', y='Series', group=1) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.125,
                  axis_text=element_text(size=12),
                  legend_title=element_blank(),
                  legend_position=None)

        plot += geom_line(color='black')

        plot += geom_segment(
            df,
            aes(x='xl', xend='xr', y='yy', yend='yy'),
            size=.7,
            color='darkred',
            arrow=arrow(ends='both')
        )


        """

        plot = \
            ggplot(data) + \
            aes(x=x_axis_col, y=y_axis_col, group=1) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.0125,
                  axis_text=element_text(size=12),
                  legend_title=element_blank(),
                  legend_position=None)

        plot += geom_line(color=line_color, size=1)

        plot += geom_segment(
            segments_data,
            aes(x='xld', xend='xrd', y='yy', yend='yy'),
            size=.7,
            color=segments_color,
            arrow=arrow(ends='both')
        )

        plot = \
            plot + \
            xlab(x_lab) + \
            ylab(y_lab) + \
            ggtitle(title)

        if numerize_y:
            plot = \
                plot + \
                scale_y_continuous(labels=lambda lst: [numerize.numerize(x)
                                                       for x in lst])

        return plot

    @staticmethod
    def univariate_change(data: pd.DataFrame,
                          x_axis_col: str,
                          y_axis_col: str,
                          change_points: List,
                          numerize_y: bool = True,
                          x_lab: str = '',
                          y_lab: str = '',
                          title: str = ''):
        """


        """
        plot = \
            ggplot(data) + \
            aes(x=x_axis_col, y=y_axis_col, group=1) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.0125,
                  axis_text=element_text(size=11),
                  legend_title=element_blank(),
                  # panel_background=element_rect(fill=WHITE),
                  # plot_background=element_rect(fill=WHITE),
                  # strip_background=element_rect(fill=WHITE),
                  # legend_background=element_rect(fill=WHITE),
                  legend_position=None)

        plot += geom_line(color=PISTACHIO_HARD, size=1)

        for cp_ in change_points:
            plot += geom_vline(xintercept=pd.Timestamp(cp_.start_time),
                               linetype='dashed',
                               color=PISTACHIO_BLACK,
                               size=1.1)

        plot += ylim(data['Series'].min(), data['Series'].max() * 1.1)
        # todo seems correct, but sometimes label appears in the middle of y-axis
        plot += geom_label(label='Change Point',
                           # y=int(data['Series'].max() * .95),
                           y=data['Series'].max(),
                           fill=PISTACHIO_FILL,
                           x=pd.Timestamp(change_points[0].start_time),
                           size=11)

        if numerize_y:
            plot = \
                plot + \
                scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        plot = \
            plot + \
            xlab(x_lab) + \
            ylab(y_lab) + \
            ggtitle(title)

        return plot

    @staticmethod
    def univariate_w_support(data: pd.DataFrame,
                             x_axis_col: str,
                             y_axis_col_main: str,
                             y_axis_col_supp: str,
                             x_lab: str = '',
                             y_lab: str = '',
                             title: str = ''):

        plot = \
            ggplot(data) + \
            aes(x=x_axis_col, y=y_axis_col_main) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.0125,
                  axis_text_y=element_text(size=11),
                  axis_text_x=element_text(size=10),
                  # panel_background=element_rect(fill=WHITE),
                  # plot_background=element_rect(fill=WHITE),
                  # strip_background=element_rect(fill=WHITE),
                  # legend_background=element_rect(fill=WHITE),
                  legend_title=element_blank(),
                  legend_position='none')

        plot += geom_line(mapping=aes(x=x_axis_col, y=y_axis_col_supp),
                          size=1,
                          color=PISTACHIO_SOFT)
        plot += geom_line(size=3, color=PISTACHIO_HARD)

        plot = \
            plot + \
            xlab(x_lab) + \
            ylab(y_lab) + \
            ggtitle(title)

        plot = \
            plot + \
            scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot

    @staticmethod
    def multivariate(data: pd.DataFrame,
                     x_axis_col: str,
                     y_axis_col: str,
                     group_col: str,
                     x_lab: str = '',
                     y_lab: str = '',
                     title: str = '',
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
                  # panel_background=element_rect(fill=WHITE),
                  # plot_background=element_rect(fill=WHITE),
                  # strip_background=element_rect(fill=WHITE),
                  # legend_background=element_rect(fill=WHITE),
                  legend_title=element_blank(),
                  legend_position='top')

        plot += geom_line(size=1)

        if add_smooth:
            plot += geom_smooth()

        plot = \
            plot + \
            xlab(x_lab) + \
            ylab(y_lab) + \
            ggtitle(title)

        return plot

    @staticmethod
    def multivariate_grid(data: pd.DataFrame,
                          scales: str,
                          numerize_y: bool = True,
                          x_lab: str = '',
                          y_lab: str = '',
                          title: str = ''):

        melted_data = pd.melt(data, 'Index')

        plot = \
            ggplot(melted_data) + \
            aes(x='Index', y='value') + \
            facet_grid('variable ~.', scales=scales) + \
            theme_minimal(base_family='Palatino', base_size=12) + \
            theme(plot_margin=.0125,
                  axis_text=element_text(size=11),
                  legend_title=element_blank(),
                  # panel_background=element_rect(fill=WHITE),
                  # plot_background=element_rect(fill=WHITE),
                  # strip_background=element_rect(fill=WHITE),
                  # legend_background=element_rect(fill=WHITE),
                  strip_text=element_text(size=13),
                  legend_position='none')

        plot += geom_line(color=PISTACHIO_HARD, size=1)

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
