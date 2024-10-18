import pandas as pd
import plotnine as p9
from numerize import numerize

from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY


class PlotDensity:

    @staticmethod
    def by_pair(data: pd.DataFrame,
                x_axis_col: str,
                group_col: str,
                numerize_x: bool = True,
                numerize_y: bool = True,
                x_lab: str = '',
                y_lab: str = '',
                title: str = ''):

        COLORS = [THEME_PALETTE[THEME['hard']],
                  THEME_PALETTE[THEME['hard_alt']]]

        data_grp = data.groupby(group_col).mean().reset_index()
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
                                  color=COLORS[i],
                                  size=1.1,
                                  alpha=0.7)

        plot = plot + \
               p9.geom_density(p9.aes(y=p9.after_stat('density')), alpha=.3) + \
               p9.xlab(x_lab) + \
               p9.ylab(y_lab) + \
               p9.ggtitle(title) + \
               p9.scale_fill_manual(values=COLORS) + \
               p9.scale_color_manual(values=COLORS)

        if numerize_x:
            plot = \
                plot + \
                p9.scale_x_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        if numerize_y:
            plot = \
                plot + \
                p9.scale_y_continuous(labels=lambda lst: [f'{x:.1e}' for x in lst])

        return plot
