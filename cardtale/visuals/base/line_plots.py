from typing import List, Optional, Dict

import numpy as np
import pandas as pd
import plotnine as p9
from plotnine.geoms.geom_hline import geom_hline
from numerize import numerize

from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY

OptHLines = Optional[List[geom_hline]]


class LinePlot:
    """
    Class for creating various types of line plots.

    Methods:
        univariate(data, x_axis_col, y_axis_col, line_color, hline_color, x_lab, y_lab, title, hlines, add_smooth, ribbons):
            Creates a univariate line plot with optional smoothing and ribbons.
        univariate_change(data, x_axis_col, y_axis_col, change_points, x_lab, y_lab, title):
            Creates a univariate line plot with change points.
        univariate_w_support(data, x_axis_col, y_axis_col_main, y_axis_col_supp, x_lab, y_lab, title):
            Creates a univariate line plot with a support line.
        multivariate_grid(data, x_axis_col, scales, x_lab, y_lab, title):
            Creates a multivariate grid line plot.
    """

    @staticmethod
    def univariate(data: pd.DataFrame,
                   x_axis_col: str,
                   y_axis_col: str,
                   line_color: str = THEME_PALETTE[THEME]['hard'],
                   hline_color: str = THEME_PALETTE[THEME]['mid'],
                   x_lab: str = '',
                   y_lab: str = '',
                   title: str = '',
                   hlines: OptHLines = None,
                   add_smooth: bool = False,
                   ribbons: Optional[Dict[str, str]] = None):
        """
        Creates a univariate line plot with optional smoothing and ribbons.

        Args:
            data (pd.DataFrame): Data for the plot.
            x_axis_col (str): Column name for the x-axis.
            y_axis_col (str): Column name for the y-axis.
            line_color (str, optional): Color for the line. Defaults to THEME_PALETTE[THEME]['hard'].
            hline_color (str, optional): Color for the horizontal lines. Defaults to THEME_PALETTE[THEME]['mid'].
            x_lab (str, optional): Label for the x-axis. Defaults to ''.
            y_lab (str, optional): Label for the y-axis. Defaults to ''.
            title (str, optional): Title of the plot. Defaults to ''.
            hlines (OptHLines, optional): List of horizontal lines. Defaults to None.
            add_smooth (bool, optional): Flag to add smoothing. Defaults to False.
            ribbons (Optional[Dict[str, str]], optional): Dictionary for ribbons. Defaults to None.

        Returns:
            plotnine.ggplot: The generated line plot.
        """

        aes_ = {'x': x_axis_col, 'y': y_axis_col, 'group': 1}

        plot = \
            p9.ggplot(data) + \
            p9.aes(**aes_) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text=p9.element_text(size=12),
                     legend_title=p9.element_blank(),
                     legend_position=None)

        if add_smooth:
            plot += p9.geom_smooth(color=THEME_PALETTE[THEME]['soft'], size=5)

        plot += p9.geom_line(color=line_color, size=1)

        if hlines is not None:
            for y_inter in hlines:
                plot += geom_hline(yintercept=y_inter,
                                   linetype='dashed',
                                   color=hline_color,
                                   size=1.1)

        if ribbons is not None:
            ribbon_aes = {'ymin': ribbons['Low'], 'ymax': ribbons['High']}

            plot += p9.geom_ribbon(p9.aes(**ribbon_aes), alpha=0.2)

        plot = \
            plot + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ggtitle(title) + \
            p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x)
                                                      for x in lst])

        return plot

    @staticmethod
    def univariate_change(data: pd.DataFrame,
                          x_axis_col: str,
                          y_axis_col: str,
                          change_points: List,
                          x_lab: str = '',
                          y_lab: str = '',
                          title: str = ''):
        """
        Creates a univariate line plot with change points.

        Args:
            data (pd.DataFrame): Data for the plot.
            x_axis_col (str): Column name for the x-axis.
            y_axis_col (str): Column name for the y-axis.
            change_points (List): List of change points.
            x_lab (str, optional): Label for the x-axis. Defaults to ''.
            y_lab (str, optional): Label for the y-axis. Defaults to ''.
            title (str, optional): Title of the plot. Defaults to ''.

        Returns:
            plotnine.ggplot: The generated line plot.
        """

        cp_idx_0 = np.where(data[x_axis_col] == change_points[0])[0][0]

        aes_ = {'x': x_axis_col, 'y': y_axis_col, 'group': 1}

        plot = \
            p9.ggplot(data) + \
            p9.aes(**aes_) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text=p9.element_text(size=11),
                     legend_title=p9.element_blank(),
                     legend_position=None) + \
            p9.geom_line(color=THEME_PALETTE[THEME]['hard'], size=1)

        for cp_ in change_points:
            plot += p9.geom_vline(xintercept=cp_,
                                  linetype='dashed',
                                  color=THEME_PALETTE[THEME]['black'],
                                  size=1.1)

        plot += p9.ylim(data[y_axis_col].min(), data[y_axis_col].max() * 1.1)

        # plot = plot + \
        #        p9.geom_label(label='Change Point',
        #                      # y=int(data['Series'].max() * .95),
        #                      y=data[y_axis_col].max(),
        #                      fill=THEME_PALETTE[THEME]['fill'],
        #                      x=cp_idx_0,
        #                      size=11) + \
        #        p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst]) + \
        #        p9.xlab(x_lab) + \
        #        p9.ylab(y_lab) + \
        #        p9.ggtitle(title)

        plot = plot + \
               p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst]) + \
               p9.xlab(x_lab) + \
               p9.ylab(y_lab) + \
               p9.ggtitle(title)

        return plot

    @staticmethod
    def univariate_w_support(data: pd.DataFrame,
                             x_axis_col: str,
                             y_axis_col_main: str,
                             y_axis_col_supp: str,
                             x_lab: str = '',
                             y_lab: str = '',
                             title: str = ''):
        """
        Creates a univariate line plot with a support line.

        Args:
            data (pd.DataFrame): Data for the plot.
            x_axis_col (str): Column name for the x-axis.
            y_axis_col_main (str): Column name for the main y-axis.
            y_axis_col_supp (str): Column name for the support y-axis.
            x_lab (str, optional): Label for the x-axis. Defaults to ''.
            y_lab (str, optional): Label for the y-axis. Defaults to ''.
            title (str, optional): Title of the plot. Defaults to ''.

        Returns:
            plotnine.ggplot: The generated line plot.
        """

        aes1_ = {'x': x_axis_col, 'y': y_axis_col_main}
        aes2_ = {'x': x_axis_col, 'y': y_axis_col_supp}

        plot = \
            p9.ggplot(data) + \
            p9.aes(**aes1_) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text_y=p9.element_text(size=11),
                     axis_text_x=p9.element_text(size=10),
                     legend_title=p9.element_blank(),
                     legend_position='none')

        plot = \
            plot + \
            p9.geom_line(mapping=p9.aes(**aes2_), size=1, color=THEME_PALETTE[THEME]['soft']) + \
            p9.geom_line(size=3, color=THEME_PALETTE[THEME]['hard']) + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ggtitle(title) + \
            p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot

    @staticmethod
    def multivariate_grid(data: pd.DataFrame,
                          x_axis_col: str,
                          scales: str,
                          category_list: Optional[List[str]] = None,
                          x_lab: str = '',
                          y_lab: str = '',
                          title: str = ''):
        """
        Creates a multivariate grid line plot.

        Args:
            data (pd.DataFrame): Data for the plot.
            x_axis_col (str): Column name for the x-axis.
            scales (str): Scales for the facets.
            category_list (Optional[List[str]], optional): List of categories. Defaults to None.
            x_lab (str, optional): Label for the x-axis. Defaults to ''.
            y_lab (str, optional): Label for the y-axis. Defaults to ''.
            title (str, optional): Title of the plot. Defaults to ''.

        Returns:
            plotnine.ggplot: The generated grid line plot.
        """

        melted_data = pd.melt(data, x_axis_col)

        if category_list is not None:
            melted_data['variable'] = pd.Categorical(melted_data['variable'], categories=category_list)

        aes_ = {'x': x_axis_col, 'y': 'value'}
        facet_ = {'rows': 'variable ~.', 'scales': scales}

        plot = \
            p9.ggplot(melted_data) + \
            p9.aes(**aes_) + \
            p9.facet_grid(**facet_) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text=p9.element_text(size=11),
                     legend_title=p9.element_blank(),
                     strip_text=p9.element_text(size=13),
                     legend_position='none') + \
            p9.geom_line(color=THEME_PALETTE[THEME]['hard'], size=1) + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ggtitle(title) + \
            p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot
