"""
Model for sensor
"""
import datetime
from flask import url_for
from sqlalchemy.dialects.postgresql import JSON

from app import db
from app.remote import usgs
from .sample import Sample


class Sensor(db.Model):
    """
    A single sensor value for a Gage

    Arguments:
        id (int): Primary key for Sensor
        gage_id (int): Foreign ``Gage``.id for the Gage that this Sensor is a part of
        gage: ``Gage`` object for associated Gage
        stype (str): Type of sensor as reported by sending station (gage).
        name (str): Nice display name for sensor
        slug (str): slug for url
        prefix (str): Prefix for value display
        suffix (str): Suffix for value display
        local (boolean): True if the station(gage) sends this sensor's data to the server.
        remote_type (str): Type of remote sensor. Currently only ``'usgs'`` is valid.
        remote_id (int): String element that should be used to query remote sensor.
        remote_parameter (str): Parameter that is required to query remote sensor.
        last (datetime): Last time data was received or retrieved.
        title (str): Title to display on plots.
        xlabel (str): x-axis label to display on plots.
        ylabel (str): y-axis label to display on plots.
        info (JSON): JSON with more detail about sensor for possible future use.
        description (text): Long description of sensor that can contain HTML or Markdown within reason.
        backend_notes (text): Backend info for admins.
        minimum (float): Lowest measurement of sensor. Used for plot formatting.
        maximum (float): Highest measurement of sensor. Used for plot formatting.
        started (datetime): Datetime that sample collection started.
        ended (datetime): Datetime that sample collection ended.
        samples: List of ``Sample`` objects from Sensor.
    """
    __tablename__ = 'sensors'

    id = db.Column(db.Integer, primary_key=True)

    gage_id = db.Column(db.Integer, db.ForeignKey('gages.id'))
    gage = db.relationship('Gage',
                           backref=db.backref('sensors', lazy='dynamic'))

    stype = db.Column(db.String(80))
    name = db.Column(db.String(80))
    slug = db.Column(db.String(40))
    prefix = db.Column(db.String(10))
    suffix = db.Column(db.String(10))
    local = db.Column(db.Boolean)
    remote_type = db.Column(db.String)
    remote_id = db.Column(db.String)
    remote_parameter = db.Column(db.String)
    last = db.Column(db.DateTime)
    title = db.Column(db.String)
    xlabel = db.Column(db.String)
    ylabel = db.Column(db.String)
    info = db.Column(JSON)
    description = db.Column(db.Text)
    backend_notes = db.Column(db.Text)
    minimum = db.Column(db.Float)
    maximum = db.Column(db.Float)
    started = db.Column(db.DateTime)
    ended = db.Column(db.DateTime)

    def timediff(self, dateTime):
        delta = datetime.datetime.now()-datetime.timedelta(minutes=60)
        return (self.stype,
                str(dateTime),
                str(datetime.datetime.now()),
                str(dateTime > delta),
                str(datetime.datetime.now() - dateTime))

    def recent(self):
        """
        Return recent sample value.
        """
        delta = datetime.datetime.now()-datetime.timedelta(minutes=60)
        # print delta
        sample = Sample.query.filter_by(sensor_id=self.id).order_by(Sample.datetime.desc()).first()
        if sample is not None and (self.local is True or sample.datetime > delta):
            # print self.timediff(sample.datetime), 'A'
            return sample
        elif sample is not None and self.local is False and sample.datetime < delta:
            # print self.timediff(sample.datetime), 'B'
            if self.remote_parameter is None:
                # print self.timediff(sample.datetime), 'C'
                usgs.get_samples(self,
                                 self.remote_id,
                                 startDT=sample.datetime,
                                 endDT=datetime.datetime.utcnow())
            else:
                # print self.timediff(sample.datetime), 'D'
                usgs.get_samples(self,
                                 self.remote_id,
                                 startDT=sample.datetime,
                                 endDT=datetime.datetime.utcnow(),
                                 parameter=self.remote_parameter)
            # print self.timediff(sample.datetime), 'E'
            return Sample.query.filter_by(sensor_id=self.id).order_by(Sample.datetime.desc()).first()
        elif sample is None and self.local is False:
            # print self.timediff(sample.datetime), 'F'
            if self.remote_parameter is None:
                print self.timediff(sample.datetime), 'G'
                usgs.get_samples(self,
                                 self.remote_id,
                                 period='P7D')
            else:
                print self.timediff(sample.datetime), 'H'
                usgs.get_samples(self,
                                 self.remote_id,
                                 period='P7D',
                                 parameter=self.remote_parameter)
            # print self.timediff(sample.datetime), 'I'
            return Sample.query.filter_by(sensor_id=self.id).order_by(Sample.datetime.desc()).first()
        else:
            # print self.timediff(sample.datetime), 'J'
            pass

    def to_json(self):
        """
        Creates a JSON object from sensor. Used where multiple sensors may be
        displayed at once.
        """
        json_post = {
            'id': self.id,
            'type': self.stype,
            'url': url_for('api.get_sensor', id=self.id, _external=True)
        }
        return json_post

    def to_long_json(self):
        """
        Creates a JSON object from sensor. Used where a single sensor will be
        displayed.
        """
        sample = Sample.query.filter_by(sensor_id=self.id).order_by(Sample.datetime.desc()).first()
        json_post = {
            'id': self.id,
            'type': self.stype,
            'description': self.description,
            'minimum': self.minimum,
            'maximum': self.maximum,
            'started': self.started,
            'ended': self.ended,
            'url': url_for('api.get_sensor', id=self.id, _external=True),
            'gage': self.gage.to_json(),
            'recent_sample': sample.to_sensor_json()
        }
        return json_post

    def to_gage_json(self):
        """
        Creates a JSON object from sensor. Displayed with gage JSON and includes
        most recent sample.
        """
        sample = Sample.query.filter_by(sensor_id=self.id).order_by(Sample.datetime.desc()).first()
        json_post = {
            'id': self.id,
            'type': self.stype,
            'url': url_for('api.get_sensor', id=self.id, _external=True),
            'recent_sample': sample.to_sensor_json()
        }
        return json_post

    def to_sample_json(self):
        """
        Creates a JSON object from sensor. Displayed with sample JSON and
        includes gage information.
        """
        json_sensor = {
            'id': self.id,
            'type': self.stype,
            'gage': self.gage.to_json(),
            'url': url_for('api.get_sensor', id=self.id, _external=True)
        }
        return json_sensor

    def __repr__(self):
        return '<Sensor %r>' % self.id
