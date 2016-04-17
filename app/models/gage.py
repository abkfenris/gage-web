"""
Gage model
"""
from flask import url_for
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

from app.database import db
from .sensor import Sensor
from .sample import Sample


gages_regions = db.Table('gages_regions',
    db.Column('gage', db.Integer, db.ForeignKey('gages.id')),
    db.Column('region', db.Integer, db.ForeignKey('regions.id'))
)


class Gage(db.Model):
    """
    A Gage is a collection of Sensors at a single location.

    Arguments:
        id (int): Primary key for Gage
        name (string): Nice name for gage
        slug (string): slug used in url
        point (Point): PostGIS Point object. Accepts WKT.
        river_id (int): Foreign key of ``River``.id that the Gage is on.
        river: ``River`` object
        user_id (int): Foreign key of ``User``.id that 'owns' the Gage.
        user: ``User`` object that `owns` the gage.
        visible (boolean): Allows a gage to not be seen on the front end
        zipcode (string): Zip code used to get the weather.
        local_town (string): Local town name, primarily used for getting the weather
        location (string): Descriptive location, often used when Gage is displayed on other pages
        elevation (int): The elevation of the Gage
        elevationUnits (string): Feet or Meters?
        backend_notes (text): Backend info for the Gage for admins.
        started (datetime): When samples started to be collected at this gage
        ended (datetime): If sampling at this gage has stopped, when?
        description (text): Long description for Gage that can contain HTML or Markdown within reason.
        key (string): Secret key that samples are signed with
        short_description (text): Short description for showing on other pages.
        regions: List of ``Region`` objects that this Gage is in.
        sensors: List of ``Sensor`` objects that are part of this Gage.
    """
    __tablename__ = 'gages'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    slug = db.Column(db.String(80), unique=True)
    # primary_sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    point = db.Column(Geometry('POINT', 4326))

    river_id = db.Column(db.Integer, db.ForeignKey('rivers.id'))
    river = db.relationship('River', backref='gages')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='gages')

    visible = db.Column(db.Boolean)
    zipcode = db.Column(db.String)
    local_town = db.Column(db.String)
    location = db.Column(db.Text)
    elevation = db.Column(db.Integer)
    elevationUnits = db.Column(db.String)
    backend_notes = db.Column(db.Text)
    started = db.Column(db.DateTime)
    ended = db.Column(db.DateTime)
    description = db.Column(db.Text)
    short_description = db.Column(db.Text)
    key = db.Column(db.String)

    regions = db.relationship('Region',
                              secondary=gages_regions,
                              backref=db.backref('gages', lazy='dynamic'))

    def latlon(self):
        """
        Returns a shapely point
        gage.latlon().y for latitude
        gage.latlon().x for longitude
        """
        latlon_point = to_shape(self.point)
        return latlon_point

    def to_json(self):
        """
        Creates a JSON Object from Gage. Used where multiple gages may be
        listed at once.
        """
        json_post = {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'html': url_for('main.gagepage',
                            slug=self.slug,
                            _external=True),
            'url': url_for('api.get_gage',
                           gid=self.id,
                           _external=True)
        }
        return json_post

    def to_long_json(self):
        """
        Cretes a JSON Object from Gage. Used where a single gage is displayed.
        """
        json_post = {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'url': url_for('api.get_gage',
                           gid=self.id,
                           _external=True),
            'html': url_for('main.gagepage',
                            slug=self.slug,
                            _external=True),
            'sensors': [sensor.to_gage_json() for sensor in self.sensors],
            'regions': [region.to_json() for region in self.regions]
        }
        return json_post

    def geojson(self):
        """
        Creates a GeoJSON Feature from the gage
        """
        point = self.latlon()
        geojson = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [point.x, point.y]
            },
            'properties': {
                'name': self.name,
                'location': self.location,
                'id': self.id,
                'html': url_for('main.gagepage',
                                slug=self.slug,
                                _external=True),
                'sensors': [sensor.to_gage_json() for sensor in self.sensors],
                'regions': [region.to_json() for region in self.regions]
            }
        }
        return geojson

    def new_sample(self, stype, value, sdatetime):
        """
        Process a new sample for the gage, and finds the right ``Sensor`` that
        the ``Sample`` should be connected to. If no ``Sensor`` exists for the
        type of sample, then a new one is created.

        Arguments:
            stype (str): Sensor type
            value (float): Sample value
            sdatetime (datetime): Sample ``datetime`` object
        """
        sensor = Sensor.query.filter_by(gage_id=self.id).filter_by(stype=stype).first()
        if sensor == None:
            sensor = Sensor(gage_id=self.id,
                            stype=stype,
                            local=True)
            db.session.add(sensor)
            db.session.commit()
        sample = Sample(sensor_id=sensor.id, value=value, datetime=sdatetime)
        db.session.add(sample)
        db.session.commit()
        return sample

    def __repr__(self):
        return '<Gage %r>' % self.name
