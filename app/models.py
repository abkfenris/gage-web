from . import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import JSON
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from remote import usgs

sections_regions = db.Table('sections_regions',
	db.Column('section', db.Integer, db.ForeignKey('sections.id')),
	db.Column('region', db.Integer, db.ForeignKey('regions.id'))
)

gages_regions = db.Table('gages_regions',
	db.Column('gage', db.Integer, db.ForeignKey('gages.id')),
	db.Column('region', db.Integer, db.ForeignKey('regions.id'))
)

rivers_regions = db.Table('rivers_regions',
	db.Column('river', db.Integer, db.ForeignKey('rivers.id')),
	db.Column('region', db.Integer, db.ForeignKey('regions.id'))
)

class Correlation(db.Model):
	"""
	Connects sections to sensors with extra data about values and how fast they should change.
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

class User(db.Model):
	__tablename__ = 'users'
	
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	email = db.Column(db.String(120), unique=True)
	password_hash = db.Column(db.String(128))
	
	@property
	def password(self):
		raise AttributeError('password is not a readable atribute')
	
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)
	
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	# def __init__(self, username, email):
	# 	self.username = username
	# 	self.email = email
	
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
	
	def to_json(self):
		json_region = {
			'id' : self.id,
			'name' : self.name,
			'url' : url_for('api.get_region', id=self.id, _external=True),
			'html': url_for('main.regionpage', slug=self.slug, _external=True),
		}
		return json_region
	
	def to_long_json(self):
		json_region = {
			'id' : self.id,
			'name' : self.name,
			'description' : self.description,
			'sections': [section.to_json() for section in self.sections],
			'gages': [gage.to_json() for gage in self.gages],
			'url': url_for('api.get_region', id=self.id, _external=True),
			'html': url_for('main.regionpage', slug=self.slug, _external=True)
		}
		return json_region
	
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
	
	regions = db.relationship('Region', secondary=rivers_regions,
	                          backref=db.backref('rivers', lazy='dynamic'))
	
	def __init__(self, name, slug, description, 
				short_description, header_image, parent):
		self.name = name
		self.slug = slug
		self.description = description
		self.short_description = short_description
		self.header_image = header_image
		self.parent = parent
	
	def to_json(self):
		json_river = {
			'id': self.id,
			'name': self.name,
			'url': url_for('api.get_river', id=self.id, _external=True),
		}
		return json_river
	
	def to_long_json(self):
		json_river = {
			'id': self.id,
			'name': self.name,
			'url': url_for('api.get_river', id=self.id, _external=True),
			'sections': [section.to_json() for section in self.sections],
			'downstream': self.parent.to_json(),
			'tributaries': [river.to_json() for river in self.tributary],
			'gages': [gage.to_json() for gage in self.gages]
		}
		return json_river
	
	def __repr__(self):
	    return '<River %r>' % self.name

class Section(db.Model):
	__tablename__ = 'sections'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80))
	slug = db.Column(db.String(40), unique=True)
	
	river_id = db.Column(db.Integer, db.ForeignKey('rivers.id'))
	river = db.relationship('River', backref='sections')
	
	#sensors = db.relationship('Sensor', secondary=correllations, backref=db.backref('sections', lazy='dynamic'))
	
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
		json_section = {
			'id' : self.id,
			'name' : self.name,
			'url': url_for('api.get_section', id=self.id, _external=True)
		}
		return json_section
	
	def to_long_json(self):
		json_section = {
			'id': self.id,
			'name': self.name,
			'url': url_for('api.get_section', id=self.id, _external=True),
			'regions': [region.to_json() for region in self.regions],
			'description': self.description,
			'access': self.access,
			'location': self.location,
			'latitude': self.inlatlon().y,
			'longitude': self.inlatlon().x,
		}
		return json_section
	
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
	
	regions = db.relationship('Region', secondary=gages_regions,
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
		json_post = {
			'id': self.id,
			'name': self.name,
			'location': self.location,
			'url' : url_for('api.get_gage', 
							id=self.id, 
							_external=True)
		}
		return json_post
	
	def to_long_json(self):
		json_post = {
			'id': self.id,
			'name': self.name,
			'location': self.location,
			'url' : url_for('api.get_gage', 
							id=self.id, 
							_external=True),
			'html': url_for('main.gagepage', 
							slug=self.slug, 
							_external=True),
			'sensors': [sensor.to_gage_json() for sensor in self.sensors],
			'regions': [region.to_json() for region in self.regions]
		}
		return json_post
	
	def new_sample(self, stype, value, sdatetime):
		sensor = Sensor.query.filter_by(gage_id=self.id).filter_by(stype=stype).first()
		if sensor == None:
			sensor = Sensor(gage_id=self.id,
							stype=stype,
							local=True)
			db.session.add(sensor)
			db.session.commit()
		sample = Sample(sensor_id=sensor.id, value=value, datetime=sdatetime )
		db.session.add(sample)
		db.session.commit()
		return sensor.id, sensor.stype
	
	def __repr__(self):
		return '<Gage %r>' % self.name

class Sensor(db.Model):
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
	
	def recent(self):
		sample = Sample.query.filter_by(sensor_id=self.id).order_by(Sample.datetime.desc()).first()
		if sample is not None:
			return sample.value
		elif sample is None and self.local is False:
			if self.remote_parameter is None:
				usgs.get_samples(self, self.remote_id, period='P7D')
			else:
				usgs.get_samples(self, self.remote_id, period='P7D', parameter=self.remote_parameter)
		else:
			pass
	
	def to_json(self):
		json_post = {
			'id' : self.id,
			'type': self.stype,
			'url' : url_for('api.get_sensor', id=self.id, _external=True)
		}
		return json_post
	
	def to_long_json(self):
		sample = Sample.query.filter_by(sensor_id=self.id).order_by(Sample.datetime.desc()).first()
		json_post = {
			'id' : self.id,
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
		sample = Sample.query.filter_by(sensor_id=self.id).order_by(Sample.datetime.desc()).first()
		json_post = {
			'id' : self.id,
			'type': self.stype,
			'url': url_for('api.get_sensor', id=self.id, _external=True),
			'recent_sample': sample.to_sensor_json()
		}
		return json_post
	
	def to_sample_json(self):
		json_sensor = {
			'id' : self.id,
			'type' : self.stype,
			'gage': self.gage.to_json(),
			'url': url_for('api.get_sensor', id=self.id, _external=True)
		}
		return json_sensor
	
	def __repr__(self):
		return '<Sensor %r>' % self.id

class Sample(db.Model):
	__tablename__ = 'samples'
	
	id = db.Column(db.Integer, primary_key=True)
	
	sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'))
	sensor = db.relationship('Sensor', backref=db.backref('samples'))
	
	datetime = db.Column(db.DateTime)
	value = db.Column(db.Float)
	
	def to_json(self):
		json_sample = {
			'id': self.id,
			'sensor': self.sensor.to_sample_json(),
			'value': self.value,
			'datetime': self.datetime,
			'url': url_for('api.get_sample', id=self.id, _external=True)
		}
		return json_sample
	
	def to_sensor_json(self):
		json_sample = {
			'id': self.id,
			'value': self.value,
			'datetime': self.datetime,
			'url': url_for('api.get_sample', id=self.id, _external=True)
		}
		return json_sample
	
	def __repr__(self):
		return '<Sample %r>' % self.id