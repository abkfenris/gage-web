#!/usr/bin/python

'''
REST methods
HTTP Method	URI													Action
GET			http://[hostname]/[version]/gage					Retrieve list of gages
GET			http://[hostname]/[version]/gage/[gageID]			Retrieve gage details
GET			http://[hostname]/[version]/gage/[gageID]/recent	Retrieve most recent sample value
POST		http://[hostname]/[version]/gage/[gageID]/sample	Create a new sample


Gage fields
name
location
description
latitude
longitude
elevation
elevationUnits

'''

from flask import Flask, make_response, send_file, request, Response
from flask_peewee.db import Database
import datetime
from peewee import *
from flask_peewee.auth import Auth
from flask_peewee.admin import Admin, ModelAdmin
from flask.ext import restful
from flask.ext.restful import reqparse, fields
from hashlib import md5
from functools import wraps
import random
import StringIO



# configure our database
DATABASE = {
	'name': 'serve.db',
	'engine': 'peewee.SqliteDatabase'
}
# DEBUG = True
SECRET_KEY = 'd5e0c$ad014641ac71aa00b5f0b80e5d540cc14251b05d'

app = Flask(__name__)
app.config.from_object(__name__)
# start building the rest api
api = restful.Api(app)

# instantiate the db wrapper
db = Database(app)

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
	
class GageAdmin(ModelAdmin):
	columns = ('name','location')

class Sample(db.Model):
	gage = ForeignKeyField(Gage, related_name='samples')
	timestamp = DateTimeField()
	level = FloatField()
	battery = FloatField()

class SampleAdmin(ModelAdmin):
	columns = ('gage', 'timestamp', 'level', 'battery')
	foreign_key_lookups = {'gage': 'name'}




	
	


auth = Auth(app, db)

admin = Admin(app, auth)
admin.register(Gage, GageAdmin)
admin.register(Sample, SampleAdmin)
auth.register_admin(admin)

admin.setup()

# start the parsers

gage_parser = reqparse.RequestParser()

sample_parser = reqparse.RequestParser()
sample_parser.add_argument('level', type=float)
sample_parser.add_argument('battery', type=float)
sample_parser.add_argument('timestamp')

class GageListAPI(restful.Resource):
	def get(self):
		output = dict() # create a dictionary to retur
		for gage in Gage.select(): 
			output[gage.id] = gage.name # add a gage id and a name for each gage to output dictionary
		return output

class GageAPI(restful.Resource): # TODO: needs to fail cleanly if the ID doesn't exist
	def get(self, id):
		output = Gage.get(Gage.id == id)
		return {'name': output.name, 'location': output.location}

# def gage_auth(f): # http://www.wiredmonk.me/customizing-flask-restful.html

from flask.ext.httpauth import HTTPBasicAuth

# auth = HTTPBasicAuth()

#@auth.verify_password
# def gage_authentication(id, password):
# 	gage = Gage.get(Gage.id == id)
# 	if not gage or not password == gage.password:
# 		return False
# 	g.user = gage
# 	return True
# 	
# 
# 
from functools import wraps
# def gage_auth(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         if not getattr(func, 'authenticated', True):
#             return func(*args, **kwargs)
# 
#         acct = gage_authentication()  # custom account lookup function
# 
#         if acct:
#             return func(*args, **kwargs)
# 
#         restful.abort(401)
#     return wrapper
	


def check_gage_auth(id, password):
    """This function is called to check if a gage id /
    password combination is valid.
    """
    gage = Gage.get(Gage.id == id)
    if not gage or not password == gage.password: 
    	return False
    return id and gage.password

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def wrong_gage():
	"""Sends a 401 response"""
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to login with proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_gage_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


class SampleAPI(restful.Resource):
	def get(self, id):
		return {'Rest API': 'SampleAPI', 'Gage': Gage.get(Gage.id == id).name}
	
	@requires_auth
	def post(self, id):
		gage = Gage.get(Gage.id == id)
		auth = request.authorization
		args = sample_parser.parse_args()
		new_sample = Sample.create(gage=gage, timestamp=args['timestamp'], level=args['level'], battery=args['battery'])
		output = dict()
		output['Gage_id'] = Gage.get(Gage.id == id).name
		output['Level'] = new_sample.level
		output['Timestamp'] = new_sample.timestamp
		output['Battery'] = new_sample.battery
		
		return output, 201

class RecentLevelAPI(restful.Resource):
	def get(self, id):
		output = dict()
		for sample in Sample.select().where(Sample.gage == id).order_by(Sample.timestamp.desc()).limit(1):
			output['Gage'] = Gage.get(Gage.id == id).name
			output['Level'] = sample.level
			output['Unit'] = Gage.get(Gage.id == id).levelUnit
			# output['Battery'] = sample.battery
		return output #{'Rest API': 'RecentLevelAPI', 'Gage': Gage.get(Gage.id == id).name, 'Level':}
	


api.add_resource(GageListAPI, '/0.1/gage', '/0.1/gage/')
api.add_resource(GageAPI, '/0.1/gage/<int:id>', '/0.1/gage/<int:id>/')
api.add_resource(SampleAPI, '/0.1/gage/<int:id>/sample')
api.add_resource(RecentLevelAPI, '/0.1/gage/<int:id>/recent') # TODO: get the most recent level from a gage

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter, datestr2num
from matplotlib import pyplot
import numpy


 

 
@app.route('/plot.png') #https://gist.github.com/wilsaj/862153
def plot():
	fig = Figure()
	ax = fig.add_subplot(1, 1, 1)
	x=[]
	y=[]
	now=datetime.datetime.now()
	delta=datetime.timedelta(days=1)
	for i in range(10):
		x.append(now)
		now+=delta
		y.append(random.randint(1, 1000))
	ax.plot_date(x, y, '-')
	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
	fig.autofmt_xdate()
	canvas=FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	response=make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response

@app.route('/gage/<int:id>/level/')
def gagelevelplot(id):
	fig = Figure()
	ax = fig.add_subplot(1, 1, 1)
	az = fig.add_subplot(1, 1, 1)
	x = []
	y = [] # need to figure out how to reverse axis
	for sample in Sample.select().where(Sample.gage == id).order_by(Sample.timestamp.desc()):
		x.append(sample.timestamp)
		y.append(sample.level)
	ax.plot(x, y, '-')
	fig.autofmt_xdate()
	ax.invert_yaxis() # remember we are looking at depth BELOW bridge
	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
	fig.suptitle('%s level in cm below gage' % Gage.get(Gage.id == id).name)
	canvas = FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	response = make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response

@app.route('/gage/<int:id>/battery/')
def gagebatteryplot(id):
	fig = Figure()
	ax = fig.add_subplot(1, 1, 1)
	x = []
	y = []
	for sample in Sample.select().where(Sample.gage == id).order_by(Sample.timestamp.desc()):
		x.append(sample.timestamp)
		y.append(sample.battery)
	ax.plot(x, y, '-')
	fig.autofmt_xdate()
	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
	fig.suptitle('%s battery potential in Volts' % Gage.get(Gage.id == id).name)
	canvas = FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	response = make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response		




if __name__ == '__main__':
	auth.User.create_table(fail_silently=True)
	Gage.create_table(fail_silently=True)
	Sample.create_table(fail_silently=True)
	app.debug = True
	app.run(host='0.0.0.0', port=5001)