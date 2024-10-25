from typing import List

from jinja2 import Environment, FileSystemLoader

from cardtale.core.data import TimeSeriesData
from cardtale.analytics.testing.base import TestingComponents
from cardtale.cards.strings import gettext

from cardtale.cards.config import (TEMPLATE_DIR,
                                   CARD_HTML,
                                   TOC_HTML,
                                   FAILED_SECTIONS_TEXT,
                                   OMITTED_SECTION_HEADER_NAME,
                                   INCLUDED_SECTIONS_TEXT)


class Card:
    """
    This is an abstract class for analysing a component of a time series

    ReportAnalyser wraps several Plots together

    """

    def __init__(self, tsd: TimeSeriesData, tests: TestingComponents):
        self.tsd = tsd
        self.tests = tests

        self.plots = {}
        self.metadata = {}
        self.show_content = True
        self.content_html = None
        self.content_pdf = None

    def analyse(self):
        """
        Analyse the Plot objects  of the component
        """
        for k in self.plots:
            self.plots[k].analyse()

        self.plots = {k: self.plots[k] for k in self.plots if self.plots[k].show_me}

        if len(self.plots) < 1:
            self.show_content = False

    def build_plots(self):
        """
        Building the plots of the component
        """

        if self.show_content:
            assert len(self.plots) > 0, 'No plots to create'

            for k in self.plots:
                if self.plots[k].show_me:
                    self.plots[k].build()
                    self.plots[k].save()

    def build_report_section(self):
        """
        Build report section

        """

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

        template_html = env.get_template(CARD_HTML)

        img_data = [self.plots[k].img_data for k in self.plots]

        header = gettext(self.metadata['section_header_str'])
        id_tag = ''.join(header.split(' ')).lower()

        self.content_html = template_html.render(
            show_content=self.show_content,
            analysis_header=gettext(self.metadata['section_header_str']),
            analysis_id=id_tag,
            analysis_introduction=gettext(self.metadata['section_intro_str']),
            img_data=img_data,
        )

    @staticmethod
    def get_organization_content(cards_to_include: List[str], cards_to_omit: List[str]):

        failed_cards = {k: FAILED_SECTIONS_TEXT[k]
                        for k in FAILED_SECTIONS_TEXT
                        if k in cards_to_omit}

        included_cards = {k: INCLUDED_SECTIONS_TEXT[k]
                          for k in INCLUDED_SECTIONS_TEXT
                          if k in cards_to_include}

        if len(included_cards):
            for i, k in enumerate(included_cards):
                included_cards[k] = included_cards[k].format(i + 2)

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

        template = env.get_template(TOC_HTML)

        content = template.render(subsection_name=OMITTED_SECTION_HEADER_NAME,
                                  included_sections=[*included_cards.values()],
                                  add_included_sections=len([*included_cards.values()]) > 0,
                                  failed_sections=[*failed_cards.values()],
                                  add_failed_sections=len([*failed_cards.values()]) > 0)

        return content
