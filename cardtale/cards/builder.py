import logging
from datetime import datetime

import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from cardtale.core.data import TimeSeriesData
from cardtale.cards.cardset.change import ChangePointCard
from cardtale.cards.cardset.seasonality import SeasonalityCard
from cardtale.cards.cardset.structural import StructuralCard
from cardtale.cards.cardset.trend import TrendCard
from cardtale.cards.cardset.variance import VarianceCard
from cardtale.cards.config import TEMPLATE_DIR, STRUCTURE_TEMPLATE
from cardtale.core.config.typing import Period
from cardtale.analytics.testing.base import TestingComponents

logging.getLogger('fontTools').setLevel(logging.ERROR)


class CardsBuilder:

    def __init__(self,
                 df: pd.DataFrame,
                 freq: str,
                 id_col: str = 'unique_id',
                 time_col: str = 'ds',
                 target_col: str = 'y',
                 period: Period = None):

        self.tsd = TimeSeriesData(df=df.copy(),
                                  freq=freq,
                                  id_col=id_col,
                                  time_col=time_col,
                                  target_col=target_col,
                                  period=period)

        self.tests = TestingComponents(self.tsd)

        self.cards = {
            'structural': StructuralCard(tsd=self.tsd, tests=self.tests),
            'trend': TrendCard(tsd=self.tsd, tests=self.tests),
            'seasonality': SeasonalityCard(tsd=self.tsd, tests=self.tests),
            'variance': VarianceCard(tsd=self.tsd, tests=self.tests),
            'change': ChangePointCard(tsd=self.tsd, tests=self.tests),
        }

        self.cards_were_analysed = False
        self.cards_to_omit = []
        self.cards_included = []

        self.plot_id = -1

        self.cards_raw_str = ''
        self.cards_raw_html = None
        self.cards_html = None

    def build_cards(self, render_html: bool = True):

        self.tests.run()

        print('Tests finished. \n Analysing results...')

        if not self.cards_were_analysed:
            for card_ in self.cards:
                self.cards[card_].analyse()

                if not self.cards[card_].show_content:
                    self.cards_to_omit.append(self.cards[card_].toc_content)
                else:
                    self.cards_included.append(self.cards[card_].toc_content)

            self.cards_were_analysed = True

        if render_html:
            self.render_doc_html()

    def render_doc_html(self):
        self.plot_id = 1

        self.cards_raw_str = ''
        for card_ in self.cards:

            self.cards[card_].build_plots()
            for plt in self.cards[card_].plots:
                self.cards[card_].plots[plt].format_caption(self.plot_id)
                self.plot_id += 1

            self.cards[card_].build_report_section()

            card_content = self.cards[card_].content_html

            self.cards_raw_str += card_content

        self._render_html_jinja()

        self.cards_html = HTML(string=self.cards_raw_html)

        return self.cards_html

    def get_pdf(self, path: str = 'EXAMPLE_OUTPUT.pdf'):
        self.cards_html.write_pdf(path)

    def _render_html_jinja(self):
        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

        template = env.get_template(STRUCTURE_TEMPLATE)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        self.cards_raw_html = template.render(toc_included=self.cards_included,
                                              toc_omitted=self.cards_to_omit,
                                              card_content=self.cards_raw_str,
                                              generation_date=current_time,
                                              series_name=self.tsd.name)
