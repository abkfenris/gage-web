"""
Model for sample
"""
from flask import url_for

from app.database import db


class Sample(db.Model):
    """
    Sample model

    Arguments:
        id (int): Primary Sample key
        sensor_id (int): Foreign ``Sensor``.id key
        sensor: ``Sensor`` object related to this sample
        datetime (datetime): ``datetime`` object of this sample (should in UTC)
        value (float): Value of sample
    """
    __tablename__ = 'samples'

    id = db.Column(db.Integer, primary_key=True)

    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), index=True)
    sensor = db.relationship('Sensor', backref=db.backref('samples'))

    datetime = db.Column(db.DateTime, index=True)
    value = db.Column(db.Float)

    def to_json(self):
        """
        Creates a JSON object from Sample. Used where multiple samples will be
        displayed at once.
        """
        json_sample = {
            'id': self.id,
            'sensor': self.sensor.to_sample_json(),
            'value': self.value,
            'datetime': self.datetime,
            'url': url_for('api.get_sample', sid=self.id, _external=True)
        }
        return json_sample

    def to_sensor_json(self):
        """
        Creates a JSON object from Sample for used with Sensor JSON.
        """
        json_sample = {
            'id': self.id,
            'value': self.value,
            'datetime': str(self.datetime),
            'url': url_for('api.get_sample', sid=self.id, _external=True)
        }
        return json_sample

    def __repr__(self):
        return '<Sample %r>' % self.id
