import pandas as pd
# from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from cardtale.core.data import TimeSeriesData
from cardtale.cards.cardset.change import ChangePointCard
from cardtale.cards.cardset.seasonality import SeasonalityCard
from cardtale.cards.cardset.structural import StructuralCard
from cardtale.cards.cardset.trend import TrendCard
from cardtale.cards.cardset.variance import VarianceCard
from cardtale.cards.cardset.base import Card
from cardtale.cards.config import TEMPLATE_DIR, STRUCTURE_TEMPLATE
from cardtale.core.config.typing import Period
from cardtale.analytics.testing.base import TestingComponents


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

        self.cards_raw_html = None
        self.cards_html = None

    def build_cards(self, render_html: bool = True):

        self.tests.run()

        print('Tests finished. \n Analysing results...')

        if not self.cards_were_analysed:
            for card_ in self.cards:
                self.cards[card_].analyse()

                if not self.cards[card_].show_content:
                    self.cards_to_omit.append(card_)
                else:
                    self.cards_included.append(card_)

            self.cards_were_analysed = True

        if render_html:
            self.render_doc_html()

    def render_doc_html(self):
        self.plot_id = 1

        deck_content = ''
        for card_ in self.cards:

            self.cards[card_].build_plots()
            for plt in self.cards[card_].plots:
                self.cards[card_].plots[plt].format_caption(self.plot_id)
                self.plot_id += 1

            self.cards[card_].build_report_section()

            card_content = self.cards[card_].content_html

            if card_ == 'structural':
                card_content += Card.get_organization_content(self.cards_included, self.cards_to_omit)

            deck_content += card_content

        self._render_html_jinja(toc_content='', card_content=deck_content)

        self.cards_html = HTML(string=self.cards_raw_html)  # .write_pdf("output.pdf")

        return self.cards_html

    def get_pdf(self, path: str = 'EXAMPLE_OUTPUT.pdf'):
        self.cards_html.write_pdf(path)

    def _render_html_jinja(self, toc_content, card_content):
        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

        template = env.get_template(STRUCTURE_TEMPLATE)

        self.cards_raw_html = template.render(toc_content=toc_content,
                                              card_content=card_content)

    # @staticmethod
    # def generate_toc(html_content: str):
    #     """
    #
    #     :param html_content:
    #     :return:
    #     """
    #
    #     soup = BeautifulSoup(html_content, 'html.parser')
    #     # headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    #     headings = soup.find_all(['h2'])
    #
    #     toc = ['<h2>Contents</h2>', '<ul class="toc">']
    #     current_level = 0
    #
    #     for heading in headings:
    #         level = int(heading.name[1])
    #
    #         if level > current_level:
    #             toc.append('<ul>' * (level - current_level))
    #         elif level < current_level:
    #             toc.append('</ul>' * (current_level - level))
    #
    #         heading_id = heading.get('id', '')
    #         if not heading_id:
    #             heading_id = re.sub(r'\W+', '-', heading.text.lower())
    #             heading['id'] = heading_id
    #
    #         toc.append(f'<li><a href="#{heading_id}">{heading.text}</a></li>')
    #         current_level = level
    #
    #     toc.append('</ul>' * current_level)
    #     toc.append('</ul>')
    #
    #     toc_html = '\n'.join(toc)
    #
    #     return toc_html
