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
    """
    Class for building and rendering analysis cards for time series data.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        tests (TestingComponents): Testing components for the time series data.
        cards (dict): Dictionary of card objects for different analyses.
        cards_were_analysed (bool): Flag indicating if the cards were analysed.
        cards_to_omit (list): List of cards to omit from the report.
        cards_included (list): List of cards to include in the report.
        cards_raw_str (str): Raw HTML string of the cards.
        cards_raw_html (str): Rendered HTML string of the cards.
        cards_html (HTML): HTML object for the cards.
        plot_id (int): ID for the plots.
    """

    def __init__(self,
                 df: pd.DataFrame,
                 freq: str,
                 id_col: str = 'unique_id',
                 time_col: str = 'ds',
                 target_col: str = 'y',
                 period: Period = None):
        """
        Initializes the CardsBuilder with the given data and parameters.

        Args:
            df (pd.DataFrame): DataFrame containing the time series data.
            freq (str): Frequency of the time series data.
            id_col (str, optional): Column name for unique identifier. Defaults to 'unique_id'.
            time_col (str, optional): Column name for time. Defaults to 'ds'.
            target_col (str, optional): Column name for target variable. Defaults to 'y'.
            period (Period, optional): Period for the time series data. Defaults to None.
        """

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
        self.cards_raw_str = ''
        self.cards_raw_html = None
        self.cards_html = None

        self.plot_id = -1

    def build_cards(self, render_html: bool = True):
        """
        Builds the analysis cards and optionally renders them to HTML.

        Args:
            render_html (bool, optional): Flag to render the cards to HTML. Defaults to True.
        """

        self.tests.run()

        print('Tests finished. \n Analysing results...')

        if not self.cards_were_analysed:

            for _, card in self.cards.items():
                card.analyse()

                if not card.show_content:
                    self.cards_to_omit.append(card.toc_content)
                else:
                    self.cards_included.append(card.toc_content)

            self.cards_were_analysed = True

        if render_html:
            self.render_doc_html()

    def render_doc_html(self):
        """
        Renders the document to HTML using Jinja2 templates.

        Returns:
            HTML: HTML object for the rendered document.
        """

        self.plot_id = 1

        self.cards_raw_str = ''
        for card_name, card in self.cards.items():
            print(card_name)

            card.build_plots()
            for plt in card.plots:
                card.plots[plt].format_caption(self.plot_id)
                self.plot_id += 1

            card.build_report_section()

            self.cards_raw_str += card.content_html

        self._render_html_jinja()

        self.cards_html = HTML(string=self.cards_raw_html)

        return self.cards_html

    def get_pdf(self, path: str = 'EXAMPLE_OUTPUT.pdf'):
        """
        Generates a PDF from the rendered HTML.

        Args:
            path (str, optional): Path to save the PDF. Defaults to 'EXAMPLE_OUTPUT.pdf'.
        """

        self.cards_html.write_pdf(path)

    def _render_html_jinja(self):
        """
        Renders the HTML content using Jinja2 templates.
        """

        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

        template = env.get_template(STRUCTURE_TEMPLATE)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        self.cards_raw_html = template.render(toc_included=self.cards_included,
                                              toc_omitted=self.cards_to_omit,
                                              card_content=self.cards_raw_str,
                                              generation_date=current_time,
                                              series_name=self.tsd.name)
