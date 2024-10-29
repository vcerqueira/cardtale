import pandas as pd
import plotnine as p9
from numerize import numerize

from cardtale.visuals.base.summary import SummaryStatPlot
from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY


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
              add_labels: bool,
              x_lab: str = '',
              y_lab: str = '',
              title: str = '',
              add_smooth: bool = False):

        aes_ = {'x': x_axis_col, 'y': y_axis_col, 'group': group_col, 'color': group_col}
        aes_t = {'label': group_col}

        plot = \
            p9.ggplot(data) + \
            p9.aes(**aes_) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text=p9.element_text(size=10),
                     legend_title=p9.element_blank()) + \
            p9.scale_color_gradientn(colors=cls.COLOR_LIST)

        if add_smooth:
            plot += p9.geom_smooth(group=1,
                                   size=3,
                                   color='lightgray',
                                   alpha=0.4)

        plot += p9.geom_line()

        if add_labels:
            data_labs = data.groupby(group_col).apply(lambda x: x.iloc[[0, -1], :])

            plot += p9.geom_text(data=data_labs, mapping=p9.aes(**aes_t))

        plot = \
            plot + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ggtitle(title) + \
            p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot

    @staticmethod
    def sub_series(data: pd.DataFrame,
                   x_axis_col: str,
                   y_axis_col: str,
                   group_col: str,
                   x_lab: str = '',
                   y_lab: str = '',
                   title: str = ''):

        stat_by_group, _ = SummaryStatPlot.summary_by_group(data, y_axis_col, group_col, 'mean')
        stat_by_group = stat_by_group.reset_index()

        aes_ = {'x': x_axis_col, 'y': y_axis_col}
        aes_hl = {'yintercept': y_axis_col}

        plot = \
            p9.ggplot(data) + \
            p9.aes(**aes_) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text_x=p9.element_text(size=8, angle=90),
                     legend_title=p9.element_blank(),
                     strip_background_x=p9.element_text(color=THEME_PALETTE[THEME]['soft']),
                     strip_text_x=p9.element_text(size=11)) + \
            p9.geom_line() + \
            p9.facet_grid(f'. ~{group_col}') + \
            p9.geom_hline(data=stat_by_group,
                          mapping=p9.aes(**aes_hl),
                          colour=THEME_PALETTE[THEME][
                              'hard'],
                          size=1) + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ggtitle(title) + \
            p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot
