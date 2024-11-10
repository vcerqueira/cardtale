import pandas as pd
import plotnine as p9
from numerize import numerize

from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY


class PlotDensity:
    """
    Class for creating density plots.

    Methods:
        by_pair(data, x_axis_col, group_col, x_lab, y_lab, title):
            Creates a density plot by pair.
    """

    @staticmethod
    def by_pair(data: pd.DataFrame,
                x_axis_col: str,
                group_col: str,
                x_lab: str = '',
                y_lab: str = '',
                title: str = ''):
        """
        Creates a density plot by pair.

        Args:
            data (pd.DataFrame): Data for the plot.
            x_axis_col (str): Column name for the x-axis.
            group_col (str): Column name for grouping.
            x_lab (str, optional): Label for the x-axis. Defaults to ''.
            y_lab (str, optional): Label for the y-axis. Defaults to ''.
            title (str, optional): Title of the plot. Defaults to ''.

        Returns:
            plotnine.ggplot: The generated density plot.
        """

        colors = [THEME_PALETTE[THEME]['hard'],
                  THEME_PALETTE[THEME]['hard_alt']]

        n_cats = data[group_col].nunique()

        if n_cats == 3:
            colors += [THEME_PALETTE[THEME]['hard_alt2']]

        data_grp = data.groupby(group_col, observed=False).mean().reset_index()
        data_grp.set_index(group_col, inplace=True)

        aes_ = {'x': x_axis_col, 'color': group_col, 'fill': group_col}

        plot = p9.ggplot(data) + \
               p9.aes(**aes_) + \
               p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
               p9.theme(plot_margin=.0175,
                        axis_text=p9.element_text(size=12),
                        strip_text=p9.element_text(size=12),
                        legend_title=p9.element_blank(),
                        legend_position='top')

        for i, grp in enumerate(data_grp[x_axis_col]):
            plot += p9.geom_vline(xintercept=grp,
                                  linetype='dashed',
                                  color=colors[i],
                                  size=1.1,
                                  alpha=0.7)

        plot = plot + \
               p9.geom_density(p9.aes(y=p9.after_stat('density')), alpha=.3) + \
               p9.xlab(x_lab) + \
               p9.ylab(y_lab) + \
               p9.ggtitle(title) + \
               p9.scale_fill_manual(values=colors) + \
               p9.scale_color_manual(values=colors) + \
               p9.scale_x_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst]) + \
               p9.scale_y_continuous(labels=lambda lst: [f'{x:.1e}' for x in lst])

        return plot
