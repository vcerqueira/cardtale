from jinja2 import Environment, FileSystemLoader

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.cards.strings import gettext
from cardtale.cards.config import TEMPLATE_DIR, CARD_HTML


class Card:
    """
    This is an abstract class for analysing a component of a time series.

    Attributes:
        tsd (TimeSeriesData): Time series data object.
        tests (TestingComponents): Testing components for the time series data.
        plots (dict): Dictionary of Plot objects.
        metadata (dict): Metadata for the card.
        toc_content (dict): Table of contents content for the card.
        show_content (bool): Flag indicating if the content should be shown.
        content_html (str): HTML content of the card.
        content_pdf (str): PDF content of the card.
    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        """
        Initializes the Card with the given time series data and testing components.

        Args:
            tsd (TimeSeriesData): Time series data object.
            tests (TestingComponents): Testing components for the time series data.
        """

        self.tsd = tsd
        self.tests = tests

        self.plots = {}
        self.metadata = {}
        self.toc_content = {}

        self.show_content = True
        self.content_html = None
        self.content_pdf = None

    def analyse(self):
        """
        Analyse the Plot objects of the component.
        """

        for k in self.plots:
            self.plots[k].analyse()

        self.plots = {k: self.plots[k] for k in self.plots if self.plots[k].show_me}

        if len(self.plots) < 1:
            self.show_content = False

        self.set_toc_content()

    def set_toc_content(self):
        """
        Sets the table of contents content based on the analysis results.
        """

        if self.show_content:
            self.toc_content = {
                'id': self.metadata['section_id'],
                'title': gettext(self.metadata['section_header_str']),
                'message': gettext(self.metadata['section_toc_success'])
            }
        else:
            self.toc_content = {
                'id': self.metadata['section_id'],
                'title': gettext(self.metadata['section_header_str']),
                'message': gettext(self.metadata['section_toc_failure'])
            }

    def build_plots(self):
        """
        Builds the plots of the component.
        """

        if self.show_content:
            assert len(self.plots) > 0, 'No plots to create'

            for k in self.plots:
                if self.plots[k].show_me:
                    self.plots[k].build()
                    self.plots[k].save()

    def build_report_section(self):
        """
        Builds the report section for the card.
        """

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

        template_html = env.get_template(CARD_HTML)

        img_data = [self.plots[k].img_data for k in self.plots]

        self.content_html = template_html.render(
            show_content=self.show_content,
            analysis_header=gettext(self.metadata['section_header_str']),
            analysis_id=self.metadata['section_id'],
            analysis_introduction=gettext(self.metadata['section_intro_str']),
            img_data=img_data,
        )
