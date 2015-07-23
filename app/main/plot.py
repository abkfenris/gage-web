"""
Ways that a plot of a selected sensor can be displayed
"""

from flask import make_response, request
import datetime
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO

from .blueprint import main
from ..models import Gage, Sensor, Sample, Correlation, River, Section


class BasePlot(object):
    """
    Base class for all plots
    """
    def data(self):
        """
        Returns sensor data

        Defaults to data within last seven days
        """
        start, end = self.startend()
        if start and end:
            return Sample.query.filter(start < Sample.datetime,
                                       Sample.datetime < end,
                                       Sample.sensor_id == self.sid)\
                               .order_by(Sample.datetime)
        if start:
            return Sample.query.filter(start < Sample.datetime,
                                       Sample.sensor_id == self.sid)\
                               .order_by(Sample.datetime)
        seven_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        return Sample.query.filter(Sample.datetime > seven_ago,
                                   Sample.sensor_id == self.sid)\
                           .order_by(Sample.datetime)

    def startend(self):
        """
        Return datetime objects if start and end arguments are in url.
        Otherwise return None.
        """
        start = request.args.get('start')
        end = request.args.get('end')
        if start:
            start = datetime.datetime.strptime(start, '%Y%m%d')
        if end:
            end = datetime.datetime.strptime(end, '%Y%m%d')
        return (start, end)

    def _setaxislimits(self, axis, ymin, ymax):
        """
        Set limits for y axis. If not set on sensor, then use a buffer of 10%
        """
        if ymin == ymax:
            ybuff = 0.1*ymin
        else:
            ybuff = 0.1*(ymax-ymin)
        if self.sensor.minimum:
            axis.set_ylim(ymin=self.sensor.minimum)
        else:
            axis.set_ylim(ymin=ymin-ybuff)
        if self.sensor.maximum:
            axis.set_ylim(ymax=self.sensor.maximum)
        else:
            axis.set_ylim(ymax=ymax+ybuff)

    def png(self):
        """
        Returns a StringIO PNG plot for the sensor
        """
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        fig = self.matplot()
        canvas = FigureCanvas(fig)
        try:
            png_output = StringIO()
        except NameError:
            png_output = BytesIO()
        canvas.print_png(png_output)
        return png_output.getvalue()

    def jpg(self):
        """
        Returns a StringIO JPG plot for the sensor
        """
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        fig = self.matplot()
        canvas = FigureCanvas(fig)
        try:
            jpg_output = StringIO()
        except NameError:
            jpg_output = BytesIO()
        canvas.print_jpg(jpg_output)
        return jpg_output.getvalue()

    def _axisfigure(self):
        """
        Returns axis and figure
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
        ax.plot(x, y, '-')
        self._setaxislimits(ax, min(y), max(y))
        if self.sensor.name:
            ax.set_title('{0} - {1}'.format(self.sensor.gage.name, self.sensor.name))
        else:
            ax.set_title('{0} - {1}'.format(self.sensor.gage.name, self.sensor.stype.capitalize()))
        return ax, fig

    def matplot(self):
        """
        Returns a matplotlib figure for building into a plot
        """
        ax, fig = self._axisfigure()
        return fig


class SensorPlot(BasePlot):
    """
    Plot class for Sensors

    Arguments:
        gid (int): Gage.id
        stype (string): sensor type for gage

    Currently supports matplotlib, but designed to be adaptable to support bokeh
    or others

    If ?start=YYYYMMDD(&end=YYYYMMDD) argument, then the plot will use those
    dates instead of the default 7 days.
    """
    def __init__(self, gid, stype):
        self.gid = gid
        self.stype = stype.lower()
        self.sensor = Sensor.query.filter_by(gage_id=self.gid).filter_by(stype=self.stype).first_or_404()
        self.sid = self.sensor.id


class CorrelationPlot(BasePlot):
    """
    Plot class for correlations
    """
    def __init__(self, section_id, sensor_id):
        self.section_id = section_id
        self.correlation = Correlation.query.filter_by(section_id=section_id)\
                                            .filter_by(sensor_id=sensor_id)\
                                            .first_or_404()
        self.sid = sensor_id
        self.sensor = self.correlation.sensor

    def levels(self):
        """
        Return the correlated levels
        """
        return (self.correlation.minimum,
                self.correlation.low,
                self.correlation.medium,
                self.correlation.high,
                self.correlation.huge)

    def matplot(self):
        ax, fig = self._axisfigure()
        lmin, llow, lmed, lhig, lhug = self.levels()
        if lmin:
            ax.axhline(y=lmin, color='#ffffff', lw=8, ls='dashed', zorder=1)
        if llow:
            ax.axhline(y=llow, color='#fcf8e3', lw=8, ls='dashed', zorder=1)
        if lmed:
            ax.axhline(y=lmed, color='#dff0d8', lw=8, ls='dashed', zorder=1)
        if lhig:
            ax.axhline(y=lhig, color='#d9edf7', lw=8, ls='dashed', zorder=1)
        if lhug:
            ax.axhline(y=lhug, color='#f2dede', lw=8, ls='dashed', zorder=1)
        return fig


@main.route('/gage/<int:gid>/<stype>.png')
@main.route('/gage/<slug>/<stype>.png')
def gagesensorplot(stype, gid=None, slug=None):
    """**/gage/<id>/<sensor type>.png**

    Draw a PNG plot for the requested gage's sensor
    """
    if slug:
        gid = Gage.query.filter_by(slug=slug).first_or_404().id
    response = make_response(SensorPlot(gid, stype).png())
    response.headers['Content-Type'] = 'image/png'
    return response


@main.route('/gage/<int:gid>/<stype>.jpg')
@main.route('/gage/<int:gid>/<stype>.jpeg')
@main.route('/gage/<slug>/stype.jpeg')
@main.route('/gage/<slug>/stype.jpg')
def gagesensorplotjpg(stype, gid=None, slug=None):
    """**/gage/<id>/<sensor type>.jpg**
    **/gage/<id>/<sensor type>.jpeg**

    Draw a JPEG plot for the requested gage's sensor
    """
    if slug:
        gid = Gage.query.filter_by(slug=slug).first_or_404().id
    response = make_response(SensorPlot(gid, stype).jpg())
    response.headers['Content-Type'] = 'image/jpeg'
    return response


@main.route('/river/<river>/<section>/<gage>/<stype>.png')
def correlationplotpng(stype, gage, section, river):
    correlation = Correlation.query.join(Correlation.sensor)\
                                   .join(Sensor.gage)\
                                   .join(Correlation.section)\
                                   .join(Section.river)\
                                   .filter(River.slug==river,
                                           Section.slug==section,
                                           Sensor.stype==stype,
                                           Gage.slug==gage)\
                                   .first_or_404()
    print(correlation)
    response = make_response(CorrelationPlot(correlation.section.id, correlation.sensor.id).png())
    response.headers['Content-Type'] = 'image/png'
    return response
