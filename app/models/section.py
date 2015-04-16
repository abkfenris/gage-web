"""
Model for section
"""
from flask import url_for
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

from app import db


# many to many relationship table for sections and regions
sections_regions = db.Table(
    'sections_regions',
    db.Column('section', db.Integer, db.ForeignKey('sections.id')),
    db.Column('region', db.Integer, db.ForeignKey('regions.id'))
)


class Section(db.Model):
    """
    River section that is commonly paddled and possibly has a correlation developed for it.

    Arguments:
        id (int): Primary key for Section
        name (string): Nice name for section
        slug (string): slug used for url
        river_id: Foreign River.id that this section is a segment of. \
                    If a section spans multiple rivers, use the river that the gage is on.
        river: ``River`` object
        description (text): Long description for Section that can contain HTML or Markdown within reason.
        short_description (text): Short description for section for showing on other pages.
        access (string): Access restrictions or issues
        location (string): Where is it?
        putin (Point): PostGIS Point object for putin. Accepts WKT.
        takeout (Point): PostGIS Point object for takeout. Accepts WKT.
        path (Linestring): PostGIS Linestring object for river. Accepts WKT.
        in_elevation (int): Elevation of the putin
        out_elevation (int): Elevation of the takeout
        header_image (string): Header image to override default
        correlations: List of ``Correlation`` objects that connect this Section to Sensors. \
                        Can do ``section.correlations[#].sensor`` and access the sensor attributes.
    """
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    slug = db.Column(db.String(40), unique=True)

    river_id = db.Column(db.Integer, db.ForeignKey('rivers.id'))
    river = db.relationship('River', backref='sections')

    description = db.Column(db.Text)
    short_description = db.Column(db.Text)
    access = db.Column(db.String)
    location = db.Column(db.String)
    putin = db.Column(Geometry('POINT'))
    takeout = db.Column(Geometry('POINT'))
    path = db.Column(Geometry('LINESTRING'))
    in_elevation = db.Column(db.Integer)
    out_elevation = db.Column(db.Integer)
    header_image = db.Column(db.String(80))

    regions = db.relationship('Region', secondary=sections_regions,
                              backref=db.backref('sections', lazy='dynamic'))

    def inlatlon(self):
        """
        Returns a shapely point for put-in.
        section.inlatlon().y for latitude
        section.inlatlon().y for longitude
        """
        try:
            latlon_point = to_shape(self.putin)
        except AssertionError:
            return None
        return latlon_point

    def outlatlon(self):
        """
        Returns a shapely point for take-out.
        section.outlatlon().y for latitude
        section.outlatlon().x for longitude
        """
        try:
            latlon_point = to_shape(self.takeout)
        except AssertionError:
            return None
        return latlon_point

    def to_json(self):
        """
        Creates a JSON Object from Section. Used where multiple sections may be
        listed at once.
        """
        json_section = {
            'id': self.id,
            'name': self.name,
            'html': url_for('main.sectionpage',
                            slug=self.slug,
                            _external=True),
            'url': url_for('api.get_section',
                           id=self.id,
                           _external=True)
        }
        return json_section

    def to_long_json(self):
        """
        Creates a JSON Object from Section. Used where a single section is
        displayed.
        """
        json_section = {
            'id': self.id,
            'name': self.name,
            'html': url_for('main.sectionpage',
                            slug=self.slug, _external=True),
            'url': url_for('api.get_section', id=self.id, _external=True),
            'regions': [region.to_json() for region in self.regions],
            'sensors': [correlation.sensor.to_json()
                        for correlation in self.correlations],
            'gages': [correlation.sensor.gage.to_json()
                      for correlation in self.correlations],
            'description': self.description,
            'access': self.access,
            'location': self.location,
            'in_latitude': self.inlatlon().y,
            'in_longitude': self.inlatlon().x,
            'out_latitude': self.outlatlon().y,
            'out_longitude': self.outlatlon().x
        }
        return json_section

    def __repr__(self):
        return '<Section %r>' % self.name
