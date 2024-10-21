import pandas as pd
# from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from cardtale.core.data import TimeSeriesData
from cardtale.cards.analyser.change import ChangeAnalysis
from cardtale.cards.analyser.seasonality import SeasonalityAnalysis
from cardtale.cards.analyser.structural import StructuralAnalysis
from cardtale.cards.analyser.trend import TrendAnalysis
from cardtale.cards.analyser.variance import VarianceAnalysis
from cardtale.cards.analyser.base import ReportAnalyser
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

        self.sections = {
            'structural': StructuralAnalysis(tsd=self.tsd, tests=self.tests),
            'trend': TrendAnalysis(tsd=self.tsd, tests=self.tests),
            'seasonality': SeasonalityAnalysis(tsd=self.tsd, tests=self.tests),
            'variance': VarianceAnalysis(tsd=self.tsd, tests=self.tests),
            'change': ChangeAnalysis(tsd=self.tsd, tests=self.tests),
        }

        self.plot_id = -1
        self.sections_analysed = False
        self.secs_to_omit = []
        self.secs_included = []

    def build_cards(self, doc_name: str, create_doc):

        self.tests.run()

        print('Tests finished. \n Analysing results...')

        self.secs_included, self.secs_to_omit = [], []
        if not self.sections_analysed:
            for sec in self.sections:
                self.sections[sec].analyse()

                if not self.sections[sec].show_content:
                    self.secs_to_omit.append(sec)
                else:
                    self.secs_included.append(sec)

            self.sections_analysed = True

        if create_doc:
            self.build_doc()

    def build_doc(self):
        self.plot_id = 1

        body_content = ''
        for sec in self.sections:
            # sec = 'structural'

            self.sections[sec].build_plots()
            for plt in self.sections[sec].plots:
                self.sections[sec].plots[plt].format_caption(self.plot_id)
                self.plot_id += 1

            self.sections[sec].build_report_section()

            content = self.sections[sec].content_html

            if sec == 'structural':
                content += ReportAnalyser.get_organization_content(self.secs_included,
                                                                   self.secs_to_omit)

            body_content += content

        env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

        template = env.get_template(STRUCTURE_TEMPLATE)

        # toc = generate_toc(body_content)
        # print(toc)

        html_rendered = template.render(toc_content='', card_content=body_content)

        HTML(string=html_rendered).write_pdf("output.pdf")

        return html_rendered

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
