import pandas as pd

import plotnine as p9
from numerize import numerize

from cardtale.visuals.config import THEME, THEME_PALETTE, FONT_FAMILY
from cardtale.core.utils.splits import DataSplit


class SummaryStatPlot:
    """
    Mean plot & Std plot
    """

    @staticmethod
    def summary_by_group(
            data: pd.DataFrame,
            y_col: str,
            group_col: str,
            func: str):
        assert func in ['mean', 'median', 'std', 'var']

        grouped_df = data.groupby(group_col)[y_col]
        target_series = data[y_col]

        group_stat = getattr(grouped_df, func)()
        overall_stat = getattr(target_series, func)()

        return group_stat, overall_stat

    @classmethod
    def SummaryPlot(cls,
                    data: pd.DataFrame,
                    y_col: str,
                    group_col: str,
                    func: str,
                    x_lab: str = '',
                    y_lab: str = '',
                    title: str = ''):
        """
        todo Anova/kruskal post hoc comparison to check which groups differ
        todo Posso decidir mostrar a meanplot ou stdplot se uma moving average ajudar nas previsões?

        """

        print(data)
        print('y_col')
        print(y_col)

        group_stat, overall_stat = cls.summary_by_group(data=data,
                                                        y_col=y_col,
                                                        group_col=group_col,
                                                        func=func)

        group_stat_df = group_stat.reset_index()
        group_stat_df[group_col] = DataSplit.df_var_to_categorical(group_stat_df, group_col)

        aes_ = {'x': group_col, 'y': y_col, 'group': 1}

        plot = \
            p9.ggplot(group_stat_df) + \
            p9.aes(**aes_) + \
            p9.theme_minimal(base_family=FONT_FAMILY, base_size=12) + \
            p9.theme(plot_margin=.0125,
                     axis_text=p9.element_text(size=10),
                     legend_title=p9.element_blank(),
                     legend_position=None) + \
            p9.geom_line(color=THEME_PALETTE[THEME]['mid'], size=.7, linetype='dashed') + \
            p9.geom_point(color=THEME_PALETTE[THEME]['hard'], size=3) + \
            p9.geom_hline(yintercept=overall_stat,
                          linetype='solid',
                          color=THEME_PALETTE[THEME]['black'],
                          size=1.1) + \
            p9.scale_y_continuous(labels=lambda lst: [numerize.numerize(x) for x in lst]) + \
            p9.xlab(x_lab) + \
            p9.ylab(y_lab) + \
            p9.ggtitle(title)

        return plot
