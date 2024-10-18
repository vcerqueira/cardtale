import pandas as pd
import plotnine as p9
from numerize import numerize

from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY


class PartialViolinPlot:
    SHIFT = 0.15
    LSIZE = 0.8
    FILL_ALHPA = 0.7

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
                       x_lab: str = '',
                       y_lab: str = '',
                       title: str = ''):
        x = p9.stage(x_axis_col, after_scale='x+cls.SHIFT*cls.alt_sign(x)')

        aes_ = {'x': x_axis_col, 'y': y_axis_col, 'fill': x_axis_col}
        aes_m1 = {'x': p9.stage(x_axis_col, after_scale='x+cls.SHIFT*cls.alt_sign(x)')}
        aes_m2 = {'x': p9.stage(x_axis_col, after_scale='x-cls.SHIFT*cls.alt_sign(x)'), 'group': group_col}

        plot = \
            p9.ggplot(data=data, mapping=p9.aes(**aes_)) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text=p9.element_text(size=12),
                     legend_title=p9.element_blank(),
                     legend_position=None) + \
            p9.geom_violin(p9.aes(**aes_m1),
                           style='left-right',
                           alpha=cls.FILL_ALHPA,
                           size=cls.LSIZE,
                           show_legend=False) + \
            p9.geom_point(p9.aes(**aes_m2),
                          color='none',
                          alpha=cls.FILL_ALHPA,
                          size=4,
                          show_legend=False) + \
            p9.geom_boxplot(width=.15,
                            alpha=cls.FILL_ALHPA,
                            size=.5,
                            show_legend=False) + \
            p9.scale_fill_manual(values=[THEME_PALETTE[THEME]['hard'],
                                         THEME_PALETTE[THEME]['hard_alt']]) + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ggtitle(title) + \
            p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot
