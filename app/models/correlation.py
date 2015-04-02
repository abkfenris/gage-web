"""
Model for section correlation to sensor levels.
"""
from app import db


class Correlation(db.Model):
    """
    Connects sections to sensors with extra data about values and how fast they
    should change.

    Arguments:
        section_id (int): ``Section``.id for the ``Section`` that this correlation is for
        section: gives a ``Section`` object from the section_id
        sensor_id (int): ``Sensor``.id for the ``Sensor`` that is correlation is for
        sensor: gives a ``Sensor`` object from the sensor_id
        minimum (float): The minimum level according to the Sensor that can float a boat
        low (float): A normal sane low level. Below this is ELF territory.
        medium (float): The low end of a medium level.
        high (float): The top of a medium level, and starting to get padded out.
        huge (float): The difference between high and scary.
        trend_slope (float): How fast should the sensor be changing in order for us to be interested?
        trend_samples (int): How many samples should it be changing over for us to be interested?
        description (text): At some point in the future will probably display \
                            the description on the section page with the correlation. \
                            Can contain HTML or Markdown within reason.
        backend_notes (text): Admin/Gage Manager information about the gage

    """
    # Needed to be an http://docs.sqlalchemy.org/en/rel_0_9/orm/relationships.html#association-object
    __tablename__ = 'correlations'
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), primary_key=True)
    section = db.relationship('Section', backref='correlations')

    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), primary_key=True)
    sensor = db.relationship('Sensor', backref='correlations')

    minimum = db.Column(db.Float)
    low = db.Column(db.Float)
    medium = db.Column(db.Float)
    high = db.Column(db.Float)
    huge = db.Column(db.Float)
    trend_slope = db.Column(db.Float)
    trend_samples = db.Column(db.Integer)
    description = db.Column(db.Text)
    backend_notes = db.Column(db.Text)
