from typing import List

from jinja2 import Environment, FileSystemLoader

from cardtale.data.uvts import UVTimeSeries
from cardtale.cards.strings import gettext

from cardtale.cards.config import (TEMPLATE_DIR,
                                   CARD_HTML,
                                   TOC_HTML,
                                   FAILED_SECTIONS_TEXT,
                                   OMITTED_SECTION_HEADER_NAME,
                                   INCLUDED_SECTIONS_TEXT)


class ReportAnalyser:
    """
    This is an abstract class for analysing a component of a time series

    ReportAnalyser wraps several Plots together

    Attributes:
        data (UVTimeSeries): Univariate time series
        plots (dict): A set of Plot objects
        metadata (dict): Meta-data
        show_content (bool): Whether component should be shown in final report
        content_html (str): HTML str content before building report
        content_pdf (str): PDF str content before building report
    """

    def __init__(self, data: UVTimeSeries):
        self.data = data
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

        self.plots = {k: self.plots[k] for k in self.plots
                      if self.plots[k].show_me}

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

    def build_report_section(self, output_to_path: bool = False):
        """
        Build report section

        :param output_to_path: Whether to build report section (True for development mode)
        """

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR.absolute()))

        template_html = env.get_template(CARD_HTML)

        img_data = [self.plots[k].img_data for k in self.plots]

        header = gettext(self.metadata['section_header_str'])
        id_tag = ''.join(header.split(' ')).lower()
        print(id_tag)

        self.content_html = template_html.render(
            show_content=self.show_content,
            analysis_header=gettext(self.metadata['section_header_str']),
            analysis_id=id_tag,
            analysis_introduction=gettext(self.metadata['section_intro_str']),
            img_data=img_data,
        )

    @staticmethod
    def get_organization_content(sections_to_include: List[str],
                                 sections_to_omit: List[str]):

        failed_secs = {k: FAILED_SECTIONS_TEXT[k] for k in FAILED_SECTIONS_TEXT
                       if k in sections_to_omit}

        included_secs = {k: INCLUDED_SECTIONS_TEXT[k] for k in INCLUDED_SECTIONS_TEXT
                         if k in sections_to_include}

        if len(included_secs):
            for i, k in enumerate(included_secs):
                included_secs[k] = included_secs[k].format(i + 2)

        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR.absolute()))

        template = env.get_template(TOC_HTML)

        content = template.render(subsection_name=OMITTED_SECTION_HEADER_NAME,
                                  included_sections=[*included_secs.values()],
                                  add_included_sections=len([*included_secs.values()]) > 0,
                                  failed_sections=[*failed_secs.values()],
                                  add_failed_sections=len([*failed_secs.values()]) > 0
                                  )

        return content
