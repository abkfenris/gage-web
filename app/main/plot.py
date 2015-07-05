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

from . import main
from ..models import Gage, Sensor, Sample


@main.route('/gage/<int:id>/<stype>.png')
def gagesensorplot(id,
                   stype,
                   days=7,
                   start=None,
                   end=None,
                   minimum=None,
                   low=None,
                   medium=None,
                   high=None,
                   huge=None):
    """**/gage/<id>/<sensor type>.png**

    Draw a plot for the requested gage's sensor

    Defaults to drawing the previous several days, but can draw a different
    number or previous days, or by explicitly selecting a YYYYMMDD start and
    end date can plot a custom range
    """
    gage = Gage.query.get_or_404(id)
    sensor = Sensor.query.filter_by(gage_id=gage.id).filter_by(stype=stype.lower()).first_or_404()
    if end is None:
        date_end = datetime.datetime.utcnow()
    else:
        date_end = datetime.datetime.strptime(str(end), '%Y%m%d')

    if start is None:
        date_begin = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    else:
        date_begin = datetime.datetime.strptime(str(start), '%Y%m%d')

    date_pad = date_begin - datetime.timedelta(days=1)
    date_range = date_end - date_begin
    days = date_range.days
    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)
    ay = fig.add_subplot(1, 1, 1)
    x = []
    y = []  # need to figure out how to reverse axi
    for sample in Sample.query\
                        .filter_by(sensor_id=sensor.id)\
                        .order_by(Sample.datetime):
        x.append(sample.datetime)
        y.append(sample.value)
    ax.plot(x, y, '-')
    if minimum is not None:
        # Color the plot with correlation levels
        ax.axhline(minimum, color="#888888")
    if low is not None:
        ax.axhline(low, color="#8a6d3b")
    if medium is not None:
        ax.axhline(medium, color="#3c763d")
    if high is not None:
        ax.axhline(high, color="#31708f")
    if huge is not None:
        ax.axhline(huge, color="#a94442")

    # Figure out what we want to use as our sensor title
    if sensor.title is None:
        if sensor.name is None:
            fig.suptitle('%s %s' % (gage.name, sensor.stype))
        else:
            fig.suptitle('%s %s' % (gage.name, sensor.name))
    else:
        fig.suptitle(sensor.title)
    canvas = FigureCanvas(fig)
    png_output = StringIO()
    canvas.print_png(png_output)
    response = make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response
