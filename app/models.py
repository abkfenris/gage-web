from . import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import JSON

sections_regions = db.Table('sections_regions',
    db.Column('section', db.Integer, db.ForeignKey('sections.id')),
    db.Column('region', db.Integer, db.ForeignKey('regions.id'))
)

correllations = db.Table('correlations',
    db.Column('section', db.Integer, db.ForeignKey('sections.id')),
    db.Column('sensor', db.Integer, db.ForeignKey('sensors.id')),
    db.Column('minimum', db.Float),
    db.Column('low', db.Float),
    db.Column('medium', db.Float),
    db.Column('high', db.Float),
    db.Column('huge', db.Float),
    db.Column('trend_slope', db.Float),
    db.Column('trend_samples', db.Integer),
    db.Column('description', db.Text),
    db.Column('backend_notes', db.Text),
    db.Column('owner', db.Integer, db.ForeignKey('users.id'))
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    
    def __init__(self, username, email):
        self.username = username
        self.email = email
    
    def __repr__(self):
        return '<User %r>' % self.username
        
class Region(db.Model):
    __tablename__ = 'regions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    slug = db.Column(db.String(40))
    description = db.Column(db.Text)
    short_description = db.Column(db.Text)
    header_image = db.Column(db.String(80))
    
    def __repr__(self):
        return '<Region %r>' % self.name

class River(db.Model):
    __tablename__ = 'rivers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    slug = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    short_description = db.Column(db.Text)
    header_image = db.Column(db.String(80))
    
    parent_id = db.Column(db.Integer, db.ForeignKey('rivers.id'))
    parent = db.relationship('River', remote_side=id, backref='tributary')
    
    def __init__(self, name, slug, description, 
                 short_description, header_image, parent):
        self.name = name
        self.slug = slug
        self.description = description
        self.short_description = short_description
        self.header_image = header_image
        self.parent = parent
    
    def __repr__(self):
        return '<River %r>' % self.name

class Section(db.Model):
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
    
    def __repr__(self):
        return '<Section %r>' % self.name
        
class Gage(db.Model):
    __tablename__ = 'gages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    slug = db.Column(db.String(40), unique=True)
    # primary_sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    point = db.Column(Geometry('POINT'))
    
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
    visible = db.Column(db.Boolean)
    description = db.Column(db.Text)
    short_description = db.Column(db.Text)
    
    def latlon(self):
		"""
		Returns a shapely point
		gage.latlon().y for latitude
		gage.latlon().x for longitude
		"""
		latlon_point = to_shape(self.point)
		return latlon_point
	

    
    def __repr__(self):
        return '<Gage %r>' % self.name

class Sensor(db.Model):
    __tablename__ = 'sensors'
    
    id = db.Column(db.Integer, primary_key=True)

    gage_id = db.Column(db.Integer, db.ForeignKey('gages.id'))
    gage = db.relationship('Gage', 
                           backref=db.backref('sensors', lazy='dynamic'))

    stype = db.Column(db.String(80))
    local = db.Column(db.Boolean)
    remote_id = db.Column(db.String)
    info = db.Column(JSON)
    description = db.Column(db.Text)
    backend_notes = db.Column(db.Text)
    minimum = db.Column(db.Float)
    maximum = db.Column(db.Float)
    started = db.Column(db.DateTime)
    ended = db.Column(db.DateTime)
    
    def __repr__(self):
        return '<Sensor %r>' % self.id

class Sample(db.Model):
    __tablename__ = 'samples'
    
    id = db.Column(db.Integer, primary_key=True)
    
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'))
    sensor = db.relationship('Sensor', backref=db.backref('samples'))
    
    datetime = db.Column(db.DateTime)
    
    def __repr__(self):
        return '<Sample %r>' % self.id