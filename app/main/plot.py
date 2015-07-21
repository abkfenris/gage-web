"""
Ways that a plot of a selected sensor can be displayed
"""

from flask import make_response
import datetime
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from .blueprint import main
from ..models import Gage, Sensor, Sample


class SensorPlot(object):
    """
    Basic plotting structure

    Arguments:
        gid (int): Gage.id
        stype (string): sensor type for gage
    """
    def __init__(self, gid, stype):
        self.gid = gid
        self.stype = stype.lower()
        self.sid = Sensor.query.filter_by(gage_id=self.gid).filter_by(stype=self.stype).first_or_404().id

    def data(self):
        """
        Returns sensor data
        """
        return Sample.query.filter_by(sensor_id=self.sid).order_by(Sample.datetime)

    def matplot(self):
        """
        Returns a figure for building into a plot
        """
        data = self.data()
        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)
        x = []
        y = []
        for sample in data:
            x.append(sample.datetime)
            y.append(sample.value)
        ax.plot(x, y, '-')
        return fig

    def png(self):
        """
        Returns a StringIO PNG plot for the sensor
        """
        fig = self.matplot()
        canvas = FigureCanvas(fig)
        png_output = StringIO()
        canvas.print_png(png_output)
        return png_output.getvalue()

    def jpg(self):
        """
        Returns a StringIO JPG plot for the sensor
        """
        fig = self.matplot()
        canvas = FigureCanvas(fig)
        jpg_output = StringIO()
        canvas.print_jpg(jpg_output)
        return jpg_output.getvalue()


@main.route('/gage/<int:gid>/<stype>.png')
def gagesensorplot(gid, stype):
    """**/gage/<id>/<sensor type>.png**

    Draw a plot for the requested gage's sensor

    Defaults to drawing the previous several days, but can draw a different
    number or previous days, or by explicitly selecting a YYYYMMDD start and
    end date can plot a custom range
    """
    plot = SensorPlot(gid, stype)
    response = make_response(plot.png())
    response.headers['Content-Type'] = 'image/png'
    return response


@main.route('/gage/<int:gid>/<stype>.jpg')
@main.route('/gage/<int:gid>/<stype>.jpeg')
def gagesensorplotjpg(gid, stype):
    """**/gage/<id>/<sensor type>.jpg**

    Draw a plot for the requested gage's sensor

    Defaults to drawing the previous several days, but can draw a different
    number or previous days, or by explicitly selecting a YYYYMMDD start and
    end date can plot a custom range
    """
    plot = SensorPlot(gid, stype)
    response = make_response(plot.jpg())
    response.headers['Content-Type'] = 'image/jpeg'
    return response
