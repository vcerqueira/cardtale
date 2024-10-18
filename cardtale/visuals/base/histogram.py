import pandas as pd
import plotnine as p9
from numerize import numerize

from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY


class PlotHistogram:

    @staticmethod
    def univariate(data: pd.DataFrame,
                   x_axis_col: str,
                   n_bins: int,
                   x_lab: str = '',
                   y_lab: str = '',
                   title: str = ''):
        aes_ = {'x': x_axis_col}

        plot = p9.ggplot(data) + \
               p9.aes(**aes_) + \
               p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
               p9.theme(plot_margin=.015,
                        axis_text=p9.element_text(size=12),
                        legend_title=p9.element_blank(),
                        legend_position=None) + \
               p9.geom_histogram(alpha=.95,
                                 bins=n_bins,
                                 color=THEME_PALETTE[THEME]['soft'],
                                 fill=THEME_PALETTE[THEME]['hard']) + \
               p9.xlab(x_lab) + \
               p9.ylab(y_lab) + \
               p9.ggtitle(title) + \
               p9.scale_x_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst]) + \
               p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst])

        return plot
