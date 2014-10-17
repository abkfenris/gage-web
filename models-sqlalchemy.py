from sqlalchemy.ext.declaritive import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry

Base = declaritive_base()

class Users(base):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	


class Gages(Base):
	__tablename__ = 'gages'
	
	id = Column(Integer, primary_key=True)
	primary_sensor_id = Column(Integer, ForeignKey('sensors.id'))
	point = Column(Geometry('POINT'))
	river_id = Column(Integer, ForeignKey('river.id'))
	user_id = Column(Integer, ForeignKey('user.id'))
	name = Column(String)
	visible = Column(Boolean)
	displayName = Column(String)
	zipcode = Column(String) # can also be international postal codes
	local_town = Column(String) # location that 
	location = Column(String)# descriptive location
	elevation = Column(Integer)
	elevationUnit = Column(String)
	backend_notes = Column(String) # or do you do something else is sqlalchemy for long text?
	started = Column(Date)
	ended = Column(Date)
	visible
	description
	short_description

class Sensors(db.Model):
	id = Column
	gage_id = Column(foreign_key)
	local = Column(Boolean) # Is this sensor something that we are storing all samples of?
	sensor_type # null for normal sensor, could be USGS, MGS...
	unit
	remote_id = Column()
	info(JSON) # null to start with, but I want this to be flexible for possibly being used for other types of data. Someone already mentioned microhydro and solar, so a semi-structured field
	description
	minimum # what is the lowest value this sensor registers
	maximum # what is the heighest it can possibly read
	started = Column(Date)
	ended = Column(Date)
	

class Samples(db.Model):
	sensor_id(foreign_key)
	value
	
class Last_samples(db.Model): # for other types of sensors, so we don't have the query the USGS/others every damn time
	sensor_id

class River(db.Model):
	name
	slug
	description
	short_description
	header_image
	flows_into(foregn_key) # references back to river_id for another river

class Section(db.Model):
	name
	slug
	river_id(foreign_key)
	description
	short_description
	access
	location
	in_elevation
	out_elevation
	elevation_unit
	header_image

class Region(db.Model):
	name
	slug
	description
	short_description
	header_image
	
class Region_Join(db.Model):
	region_id(foreign_key)
	section_id(foreign_key)

class Correlation(db.Model):
	section_id(foreign_key)
	sensor_id(foreign_key)
	minimum # 
	low # line between elf and normal peoples low
	medium
	high
	huge
	trend_slope # how fast should the gage be changing to consider it rising or falling
	trend_samples # how many sensor values should we consider back for trend change