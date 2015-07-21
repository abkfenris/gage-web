"""
Ways that a plot of a selected sensor can be displayed
"""

from flask import make_response
import datetime
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .blueprint import main
from ..models import Gage, Sensor, Sample


class SensorPlot(object):
    """
    Base plot object for Sensors

    Arguments:
        gid (int): Gage.id
        stype (string): sensor type for gage

    Currently supports matplotlib, but designed to be adaptable to support bokeh or others
    """
    def __init__(self, gid, stype):
        self.gid = gid
        self.stype = stype.lower()
        self.sensor = Sensor.query.filter_by(gage_id=self.gid).filter_by(stype=self.stype).first_or_404()
        self.sid = self.sensor.id

    def data(self):
        """
        Returns sensor data
        """
        return Sample.query.filter_by(sensor_id=self.sid).order_by(Sample.datetime)

    def matplot(self):
        """
        Returns a matplotlib figure for building into a plot
        """
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib.figure import Figure
        import seaborn as sns
        sns.set()
        data = self.data()
        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)
        x = []
        y = []
        for sample in data:
            x.append(sample.datetime)
            y.append(sample.value)
        ymin, ymax = min(y), max(y)
        if ymin == ymax:
            ybuff = 0.1*ymin
        else:
            ybuff = 0.1*(ymax-ymin)
        ax.plot(x, y, '-')
        if self.sensor.minimum:
            ax.set_ylim(ymin=self.sensor.minimum)
        else:
            ax.set_ylim(ymin=ymin-ybuff)
        if self.sensor.maximum:
            ax.set_ylim(ymax=self.sensor.maximum)
        else:
            ax.set_ylim(ymax=ymax+ybuff)
        return fig

    def png(self):
        """
        Returns a StringIO PNG plot for the sensor
        """
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        fig = self.matplot()
        canvas = FigureCanvas(fig)
        png_output = StringIO()
        canvas.print_png(png_output)
        return png_output.getvalue()

    def jpg(self):
        """
        Returns a StringIO JPG plot for the sensor
        """
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        fig = self.matplot()
        canvas = FigureCanvas(fig)
        jpg_output = StringIO()
        canvas.print_jpg(jpg_output)
        return jpg_output.getvalue()


@main.route('/gage/<int:gid>/<stype>.png')
def gagesensorplot(gid, stype):
    """**/gage/<id>/<sensor type>.png**

    Draw a PNG plot for the requested gage's sensor
    """
    response = make_response(SensorPlot(gid, stype).png())
    response.headers['Content-Type'] = 'image/png'
    return response


@main.route('/gage/<int:gid>/<stype>.jpg')
@main.route('/gage/<int:gid>/<stype>.jpeg')
def gagesensorplotjpg(gid, stype):
    """**/gage/<id>/<sensor type>.jpg**
    **/gage/<id>/<sensor type>.jpeg**

    Draw a JPEG plot for the requested gage's sensor
    """
    response = make_response(SensorPlot(gid, stype).jpg())
    response.headers['Content-Type'] = 'image/jpeg'
    return response
