"""
Ways that a plot of a selected sensor can be displayed
"""
import datetime

from bokeh.plotting import figure
from flask import make_response, request, current_app


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

    @staticmethod
    def startend():
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


    def data_datetimes_values(self):
        """
        Returns the date as two lists, datetimes and values
        """
        datetimes, values = [], []

        data = self.data()

        for sample in data:
            datetimes.append(sample.datetime)
            values.append(sample.value)

        return datetimes, values


    def bokeh(self):
        """
        Returns a bokeh plot object
        """
        p = figure(x_axis_type='datetime', title=str(self.sensor))

        datetimes, values = self.data_datetimes_values()

        p.circle(datetimes, values, legend=self.sensor.nice_name())

        return p
    

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
        self.gid = self.sensor.gage.id


