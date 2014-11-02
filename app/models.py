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

class User(db.Model):
	"""
	User model
	
	Arguments:
		id (int): Primary User Key
		username (str): Unique username as chosen by the user
		email (str): User's email address
		password_hash (str): Users hashed password
	"""
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
		"""
		Takes user generated password and uses werkzeug.security to create a hash and stores it.
		"""
		self.password_hash = generate_password_hash(password)
	
	def verify_password(self, password):
		"""
		Verify's user's password against stored werkzeug.security hash.
		
		Arguments:
			password (str): password to check against stored hash
		"""
		return check_password_hash(self.password_hash, password)
	
	# def __init__(self, username, email):
	# 	self.username = username
	# 	self.email = email
	
	def __repr__(self):
		return '<User %r>' % self.username
        
class Region(db.Model):
	"""
	Regions where Rivers, Sections, and Gages exist
	
	Arguments:
		id (int): Primary Region Key
		name (str): Nice name
		slug (str): slug for url formatting
		description (text): Long description that can contain HTML or Markdown within reason.
		short_description (text): Short description, for showing on other pages.
		header_image (str): Header image to override default.
		rivers: List of ``River`` objects for Region.
		sections: List of ``Section`` objects for Region.
		gages: List of ``Gage`` objects for Region.
	"""
	__tablename__ = 'regions'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80))
	slug = db.Column(db.String(40))
	description = db.Column(db.Text)
	short_description = db.Column(db.Text)
	header_image = db.Column(db.String(80))
	
	def to_json(self):
		"""
		Create a JSON object from region. Used where multiple regions may be displayed simultaneously.
		"""
		json_region = {
			'id' : self.id,
			'name' : self.name,
			'url' : url_for('api.get_region', id=self.id, _external=True),
			'html': url_for('main.regionpage', slug=self.slug, _external=True),
		}
		return json_region
	
	def to_long_json(self):
		"""
		Create a JSON object from region. Used when only one region is to be displayed.
		"""
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
	"""
	River model. Rivers are rivers as we know them, \
	they have a parent that they flow downstream into and have tributaries that flow into them.
	
	Arguments:
		id (int): Primary River id
		name (string): Nice River name
		slug (string): slug for url formatting
		description (text): Long description that can contain HTML or Markdown within reason.
		short_description (text): Short description for showing on other pages.
		header_image (string): Header image to override default
		parent_id (int): River.id for the river that this one flows into
		parent: ``River`` object from parent_id
		tributary: List of ``River`` objects for any River that has this one in it's parent_id.
		regions: List of ``Region`` objects for River
		sections: List of ``Section`` objects for River
	"""
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
	
	#def __init__(self, name, slug, description, 
	#			short_description, header_image, parent):
	#	self.name = name
	#	self.slug = slug
	#	self.description = description
	#	self.short_description = short_description
	#	self.header_image = header_image
	#	self.parent = parent
	
	def to_json(self):
		"""
		Creates a JSON Object from River. Used where multiple rivers may be listed at once.
		"""
		json_river = {
			'id': self.id,
			'name': self.name,
			'url': url_for('api.get_river', id=self.id, _external=True),
		}
		return json_river
	
	def to_long_json(self):
		"""
		Creates a JSON Object from River. Used where a single river is being displayed.
		"""
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
		putin (Point): PostGIS Point object for putin
		takeout (Point): PostGIS Point object for takeout
		path (Linestring): PostGIS Linestring object for river
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
		Creates a JSON Object from Section. Used where multiple sections may be listed at once.
		"""
		json_section = {
			'id' : self.id,
			'name' : self.name,
			'url': url_for('api.get_section', id=self.id, _external=True)
		}
		return json_section
	
	def to_long_json(self):
		"""
		Creates a JSON Object from Section. Used where a single section is displayed.
		"""
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
	"""
	A Gage is a collection of Sensors at a single location.
	
	Arguments:
		id (int): Primary key for Gage
		name (string): Nice name for gage
		slug (string): slug used in url
		point (Point): PostGIS Point object
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
		short_description (text): Short description for showing on other pages.
		regions: List of ``Region`` objects that this Gage is in.
		sensors: List of ``Sensor`` objects that are part of this Gage.
	"""
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
		"""
		Creates a JSON Object from Gage. Used where multiple gages may be listed at once.
		"""
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
		"""
		Cretes a JSON Object from Gage. Used where a single gage is displayed.
		"""
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
		"""
		Process a new sample for the gage, and finds the right ``Sensor`` that the ``Sample`` should be connected to. \
		If no ``Sensor`` exists for the type of sample, then a new one is created.
		
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