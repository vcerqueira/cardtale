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
    Base class for all plots in the system

    Attributes:
        HEIGHT (float): Default height for plots.
        HEIGHT_SMALL (float): Default height for small plots.
        WIDTH (float): Default width for plots.
        WIDTH_SMALL (float): Default width for small plots.
        tsd (TimeSeriesData): Time series data for the plot.
        plot (Any): The plot object.
        name (NameOptList): Name(s) of the plot.
        multi_plot (bool): Flag indicating if the plot is a multi-plot.
        analysis (List[str]): List of analysis results.
        caption (str): Caption for the plot.
        show_me (bool): Flag indicating if the plot should be shown.
        img_data (dict): Dictionary containing image data.
        plot_name (str): Name of the plot.
        width (float): Width of the plot.
        height (float): Height of the plot.
        width_s (float): Width of the small plot.
        height_s (float): Height of the small plot.

    """

    HEIGHT = 4.5
    HEIGHT_SMALL = 5
    WIDTH = 12
    WIDTH_SMALL = 6

    def __init__(self, tsd: TimeSeriesData, name: NameOptList, multi_plot: bool):
        """
        Initializes the Plot class.

        Args:
            tsd (TimeSeriesData): Time series data for the plot.
            name (NameOptList): Name(s) of the plot.
            multi_plot (bool): Flag indicating if the plot is a multi-plot.

        """

        self.tsd = tsd
        self.name = name
        self.multi_plot = multi_plot
        self.analysis = []
        self.caption = ''
        self.show_me = False
        self.img_data = {}
        self.plot_name = ''
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.width_s = self.WIDTH_SMALL
        self.height_s = self.HEIGHT_SMALL

        if self.multi_plot:
            self.plot = {'lhs': None, 'rhs': None}
        else:
            self.plot = None
    def build(self, *args, **kwargs):
        """
        Creates the plot.

        Args:
            **kwargs: Additional keyword arguments.

        """
        raise NotImplementedError

    def analyse(self,  *args, **kwargs):
        """
        Analyzes the data to be plotted.

        Args:
            **kwargs: Additional keyword arguments.
        """
        raise NotImplementedError

    def save(self):
        """
        Saves the plot as an image and encodes it in base64.
        """

        if not self.multi_plot:

            img_code = self.get_encode(self.plot,
                                       height=self.height,
                                       width=self.width)

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
        Formats the caption with the respective number.

        Args:
            plot_id (int): Plot id.
        """
        self.img_data['caption'] = self.img_data['caption'].format(plot_id)

    @staticmethod
    def get_encode(plot, height, width):
        """
        Encodes the plot as a base64 string.

        Args:
            plot (Any): The plot object.
            height (float): Height of the plot.
            width (float): Width of the plot.

        Returns:
            str: Base64 encoded string of the plot image.
        """

        img_buffer = io.BytesIO()

        plot.save(img_buffer, height=height, width=width, format='png')
        img_buffer.seek(0)
        decode_str = base64.b64encode(img_buffer.getvalue()).decode()
        return decode_str
