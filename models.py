import datetime

from flask_peewee.auth import BaseUser
from peewee import *

from app import db

class User(db.Model, BaseUser):
	username = CharField()
	password = CharField()
	email = CharField()
	join_date = DateTimeField(default=datetime.datetime.now)
	active = BooleanField(default=True)
	admin = BooleanField(default=False)
	
	def __unicode__(self):
		return self.username

class Gage(db.Model): # TODO: add other fields that would be useful to generate config files
	name = CharField()
	location = CharField()
	password = CharField(default=md5(str(random.randint(0,9999999999999))).hexdigest()[:8])
	created = DateTimeField(default=datetime.datetime.now)
	description = TextField()
	latitude = FloatField()
	longitude = FloatField()
	elevation = IntegerField()
	elevationUnit = CharField(choices=(('ft', 'Feet'),('m', 'Meters')))
	started = DateTimeField(default=datetime.datetime.now)
	ended = DateTimeField(default=datetime.datetime(3000,1,1,1,1,1))
	levelUnit = CharField(choices=(('cm', 'Centimeters'),('in', 'Inches'),('ft', 'Feet'), ('m', 'Meters')))
	access = BooleanField(default=False)
	description = TextField(null=True)
	shortDescription = TextField()
	correlation = CharField(null=True)
	useCorrelation = BooleanField(default=False)
	jumbotronImage = CharField(null=True)
	displayName = CharField(null=True)
	runs = TextField(null=True)
	low = FloatField(null=True)
	medium = FloatField(null=True)
	high = FloatField(null=True)
	huge = FloatField(null=True)
	backendNotes = TextField(null=True)
	title = CharField(null=True)
	localTown = CharField()
	region = ForeignKeyField(Region, related_name='Gages')


class Sample(db.Model):
	gage = ForeignKeyField(Gage, related_name='samples')
	timestamp = DateTimeField()
	level = FloatField()
	battery = FloatField()

class Region(db.Model):
	name = CharField()
	description = TextField()

	