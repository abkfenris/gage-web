"""
api imports app, auth and models, but none of these import api

REST methods
HTTP Method	URI															Action
GET			http://[hostname]/[version]/gage							Retrieve list of gages
GET			http://[hostname]/[version]/gage/[gageID]					Retrieve gage details
GET			http://[hostname]/[version]/gage/[gageID]/recent			Retrieve most recent sample value
POST		http://[hostname]/[version]/gage/[gageID]/sample			Create a new sample
GET			http://[hostname]/[version]/gage/[gageID]/sample/recent		Most recent sample timestamp mainly for gages to verify what they have uploaded already

"""

from flask import Response, request
from flask.ext import restful
from flask.ext.restful import reqparse, fields
from functools import wraps
#import datetime

from app import app
from auth import auth
from models import User, Gage, Sample

api = restful.Api(app)
gage_parser = reqparse.RequestParser()

sample_parser = reqparse.RequestParser()
sample_parser.add_argument('level', type=float)
sample_parser.add_argument('battery', type=float)
sample_parser.add_argument('timestamp')

class GageListAPI(restful.Resource):
	def get(self):
		output = dict() # create a dictionary to retur
		for gage in Gage.select(): 
			output[gage.id] = gage.name, gage.location # add a gage id and a name for each gage to output dictionary
		return output

class GageAPI(restful.Resource): # TODO: needs to fail cleanly if the ID doesn't exist
	def get(self, id):
		output = Gage.get(Gage.id == id)
		return {'name': output.name, 'location': output.location}

# Authenicate the gages as they post to the REST endpoint, currently it does not match the gage to the one it's claiming to post to though... http://flask.pocoo.org/snippets/8/

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

def test_timestamp(timestamp, gage_id):
	try:
		sample = Sample.get(Sample.timestamp == timestamp, Sample.gage == gage_id)
	except Sample.DoesNotExist:
		sample = False
	return sample


class SampleAPI(restful.Resource):
	def get(self, id):
		return {'Rest API': 'SampleAPI', 'Gage': Gage.get(Gage.id == id).name}
	
	@requires_auth
	def post(self, id):
		gage = Gage.get(Gage.id == id)
		auth = request.authorization
		args = sample_parser.parse_args()
		timestamp = args['timestamp']
		existing_sample = test_timestamp(timestamp, gage)
		output = dict()
		if existing_sample == False:
			new_sample = Sample.create(gage=gage, timestamp=args['timestamp'], level=args['level'], battery=args['battery'])
			output['Timestamp'] = new_sample.timestamp
		else:
			new_sample = existing_sample
		output['Gage_id'] = Gage.get(Gage.id == id).name
		output['Level'] = new_sample.level
		output['Battery'] = new_sample.battery
		output['server_sample_id'] = new_sample.id
		
		return output, 201

class RecentLevelAPI(restful.Resource):
	def get(self, id):
		output = dict()
		for sample in Sample.select().where(Sample.gage == id).order_by(Sample.timestamp.desc()).limit(1):
			output['Gage'] = Gage.get(Gage.id == id).name
			output['Level'] = sample.level
			output['Unit'] = Gage.get(Gage.id == id).levelUnit
			# output['Battery'] = sample.battery
		return output

class RecentSampleAPI(restful.Resource):
	def get(self, id):
		output = dict()
		for sample in Sample.select().where(Sample.gage == id).order_by(Sample.timestamp.desc()).limit(1):
			output['timestamp'] = str(sample.timestamp)
		return output




# REST endpoints

api.add_resource(GageListAPI, '/0.1/gage/')
api.add_resource(GageAPI, '/0.1/gage/<int:id>/')
api.add_resource(SampleAPI, '/0.1/gage/<int:id>/sample')
api.add_resource(RecentLevelAPI, '/0.1/gage/<int:id>/recent/')
api.add_resource(RecentSampleAPI, '/0.1/gage/<int:id>/sample/recent')