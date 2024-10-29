import warnings
import io
import base64
from typing import Union, List

from plotnine.exceptions import PlotnineWarning

from cardtale.core.data import TimeSeriesData

NameOptList = Union[List[str], str]

warnings.filterwarnings('ignore', category=PlotnineWarning)


class Plot:
    """
    This is a class for plotting the series

    A plot class for analysing a specific aspect of the series.
    This class handle the plot and the respective analysis

    Attributes:
        data (UVTimeSeries): Univariate time series
        plot (dict): A dict with graphics
        multi_plot (bool): Whether the plot include a single graphic or two
        analysis (list): List of textual analysis
        file_path (str): Path where the plot is saved
        caption (str): Plot caption
        show_me (bool): Whether the plot should be included in the report
        img_data (dict): Plot meta-data
        plot_name (dict): Plot name identifier
    """

    HEIGHT = 4.5
    HEIGHT_SMALL = 5
    WIDTH = 12
    WIDTH_SMALL = 6

    def __init__(self, tsd: TimeSeriesData, name: NameOptList, multi_plot: bool):
        self.tsd = tsd
        self.plot = None
        self.name = name
        self.multi_plot = multi_plot
        self.analysis = []
        self.file_path = ''
        self.caption = ''
        self.show_me = False
        self.img_data = {}
        self.plot_name = ''
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.width_s = self.WIDTH_SMALL
        self.height_s = self.HEIGHT_SMALL

    def build(self, **kwargs):
        """
        Creating the actual plot
        """
        pass

    def analyse(self, **kwargs):
        """
        Analysing the data to be plotted
        """
        pass

    def save(self):

        if not self.multi_plot:
            print('here')

            try:
                img_code = self.get_encode(self.plot,
                                           height=self.height,
                                           width=self.width)
            except IndexError as e:
                print(self.plot)
                print(e)
                raise IndexError('---')

            self.img_data = {
                'src': img_code,
                'caption': self.caption,
                'plot_name': self.plot_name,
                'analysis': self.analysis,
                'side_by_side': False,
            }
        else:
            img_code_lhs = self.get_encode(self.plot['lhs'],
                                           height=self.height_s,
                                           width=self.width_s)

            img_code_rhs = self.get_encode(self.plot['rhs'],
                                           height=self.height_s,
                                           width=self.width_s)

            self.img_data = {
                'src_lhs': img_code_lhs,
                'src_rhs': img_code_rhs,
                'caption': self.caption,
                'plot_name': self.plot_name,
                'analysis': self.analysis,
                'side_by_side': True,
            }

    def format_caption(self, plot_id: int):
        """
        Formatting the caption with the respective number

        :param plot_id: Plot id
        """
        self.img_data['caption'] = self.img_data['caption'].format(plot_id)

    @staticmethod
    def get_encode(plot, height, width):
        img_buffer = io.BytesIO()

        plot.save(img_buffer, height=height, width=width, format='png')
        img_buffer.seek(0)
        decode_str = base64.b64encode(img_buffer.getvalue()).decode()
        return decode_str
