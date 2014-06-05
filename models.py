import datetime

from flask_peewee.auth import BaseUser
from peewee import *

from app import db

#import what the models need for functions
from math import sin, cos, sqrt, atan2, radians
from micawber import parse_html, bootstrap_basic #requires beautiful-soup to be installed first
from markdown import markdown
from flask import Markup
from hashlib import md5
import operator
import numpy
import random


#map functions needed for model fonctions
oembed = bootstrap_basic()

#build a user class, largely for 
class User(db.Model, BaseUser):
	username = CharField()
	password = CharField()
	email = CharField()
	join_date = DateTimeField(default=datetime.datetime.now)
	active = BooleanField(default=True)
	admin = BooleanField(default=False)
	
	def __unicode__(self):
		return self.username

class Region(db.Model):
	name = CharField()
	description = TextField(null=True)
	shortDescription = TextField(null=True)
	initial = CharField()
	
	def description_html(self): # from http://charlesleifer.com/blog/saturday-morning-hack-a-little-note-taking-app-with-flask/
		html = parse_html(
			markdown(self.description), 
			oembed, 
			maxwidth=690,
			urlize_all=True)
		return Markup(html)
	
	def __unicode__(self):
		return self.name # required to get the admin to actually show the name rather than the object as a foreign key
	

class Gage(db.Model): # TODO: add other fields that would be useful to generate config files
	name = CharField()
	visible = BooleanField(default=True)
	displayName = CharField(null=True)
	zipcode = TextField() # should be varchar, should not be int because it goes and drops the leading zero
	localTown = CharField()
	region = ForeignKeyField(Region, 'Gages')
	location = CharField()
	password = CharField(default=md5(str(random.randint(0,9999999999999))).hexdigest()[:8])
	description = TextField(null=True)
	shortDescription = TextField(null=True)
	runs = TextField(null=True)
	created = DateTimeField(default=datetime.datetime.now)
	latitude = FloatField()
	longitude = FloatField()
	elevation = IntegerField()
	elevationUnit = CharField(choices=(('ft', 'Feet'),('m', 'Meters')))
	sensorRange = FloatField()
	levelUnit = CharField(choices=(('cm', 'Centimeters'),('in', 'Inches'),('ft', 'Feet'), ('m', 'Meters')))
	backendNotes = TextField(null=True)
	started = DateTimeField(default=datetime.datetime.now)
	ended = DateTimeField(default=datetime.datetime(3000,1,1,1,1,1))
	access = BooleanField(default=False)
	correlation = CharField(null=True)
	useCorrelation = BooleanField(default=False)
	jumbotronImage = CharField(null=True)
	useLevels = BooleanField(default=False)
	low = FloatField(null=True)
	medium = FloatField(null=True)
	high = FloatField(null=True)
	huge = FloatField(null=True)
	trendSlope = FloatField(default=.2)
	trendSamples = FloatField(default=4)
	owner = ForeignKeyField(User, related_name='Gages')

	def __unicode__(self):
		return self.name # required to get the admin to actually show the name rather than the object as a foreign key

	
	def description_html(self): # from http://charlesleifer.com/blog/saturday-morning-hack-a-little-note-taking-app-with-flask/
		html = parse_html(
			markdown(self.description), 
			oembed, 
			maxwidth=690,
			urlize_all=True)
		return Markup(html)
	
	def runs_html(self):
		html = parse_html(
			markdown(self.runs), 
			oembed, 
			maxwidth=690,
			urlize_all=True)
		return Markup(html)
	
	def recent_level(self):
		output = float()
		for sample in Sample.select().where(Sample.gage == self.id).order_by(Sample.timestamp.desc()).limit(1):
			output = "%.2f" % (sample.level * .01) # limit float string decimal points http://stackoverflow.com/questions/455612/python-limiting-floats-to-two-decimal-points
		return output
	
	def level_trend(self, samples=4, slope=.2):
		x = []
		y = []
		if len(self.trendSlope) != 0:
			calcSlope = self.trendSlope
		else:
			pass
		if len(self.trendSamples) != 0:
			samples = self.trendSamples
		else:
			pass
		for sample in Sample.select().where(Sample.gage == self.id).order_by(Sample.timestamp.desc()).limit(samples):
			x.append(sample.id)
			y.append(sample.level)
		if len(x) == 0:
			return 'no data'
		else:
			slope, intercept = numpy.polyfit(x, y, 1)
			print slope
			if slope >= .2:
				return 'rising'
			elif .2 > slope > -.2:
				return 'steady'
			else:
				return 'falling'
	
	def level_badge(self, samples=4, slope=.2):
	
		recent = float()
		recent_raw = float()
		for sample in Sample.select().where(Sample.gage == self.id).order_by(Sample.timestamp.desc()).limit(1):
			recent = "%.2f" % (sample.level * .01) # limit float string decimal points http://stackoverflow.com/questions/455612/python-limiting-floats-to-two-decimal-points
			recent_raw = sample.level
			
		x = []
		y = []
		if not self.trendSlope:
			calcSlope = self.trendSlope
		else:
			pass
		if not self.trendSamples:
			samples = 2
		else:
			pass
		for sample in Sample.select().where(Sample.gage == self.id).order_by(Sample.timestamp.desc()).limit(samples):
			x.append(sample.id)
			y.append(sample.level)
		if len(x) == 0:
			trend = 'no data'
		else:
			slope, intercept = numpy.polyfit(x, y, 1)
			print slope
			if slope >= .2:
				trend = 'rising'
			elif .2 > slope > -.2:
				trend = 'steady'
			else:
				trend = 'falling'
				
		# make the badge, if useLevels is true for the gage color code it
		html = ''
		if self.useLevels == True:
			if recent_raw >= self.huge:
				html = '<span class="badge alert-danger">'
			elif self.huge > recent_raw >= self.high:
				html = '<span class="badge alert-info">'
			elif self.high > recent_raw >= self.medium:
				html = '<span class="badge alert-success">'
			elif self.medium > recent_raw >= self.low:
				html = '<span class="badge alert-warning">'
			else:
				html = '<span class="badge">'
		else:
			html = '<span class="label label-default" style="float:right; margin-left:6px">'
		html += ''

		# thrown an icon on the badge if it's changing
		html += str(recent)
		if trend == 'rising':
			html += '<span class="glyphicon glyphicon-arrow-up"></span>'
		elif trend == 'steady':
			html += '<span class="glyphicon glyphicon-arrow-right"></span>'
		elif trend == 'falling':
			html += '<span class="glyphicon glyphicon-arrow-down"></span>'
		else:
			pass
		html += '</span>'
		return Markup(html)
		
	def distance_from(self, id):
		other = Gage.get(Gage.id == id)
		
		R = 6373.0
		
		lat1 = radians(self.latitude)
		lon1 = radians(self.longitude)
		lat2 = radians(other.latitude)
		lon2 = radians(other.longitude)
		
		dlon = lon2 - lon1
		dlat = lat2 - lat1
		a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
		c = 2 * atan2(sqrt(a), sqrt(1-a))
		distance = R * c
		
		return distance
	
	def other_gage_distance(self):
		output = dict()
		for othergage in Gage.select().where(Gage.id != self.id):
			output[othergage.id] = self.distance_from(othergage.id)
		sorted_output = sorted(output.iteritems(), key=operator.itemgetter(1))
		return sorted_output
		

class Sample(db.Model):
	gage = ForeignKeyField(Gage, related_name='Samples')
	timestamp = DateTimeField()
	level = FloatField()
	battery = FloatField()



	