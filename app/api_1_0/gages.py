"""
gages api imports api, app, db, auth, and models

REST methods
Method	URI								Action
GET		/api/1.0/gage					Retrieve list of gages
GET		/api/1.0/gage/[Gage.id]			Retrieve Gage Details
GET		/api/1.0/gage/[Gage.id]/recent	Retrieve most recent samples
POST	/api/1.0/gage/[Gage.id]			Creates new samples

"""

from flask import jsonify, request, g, abort, url_for, current_app
from flask.ext import restful
from .. import db
from ..models import Gage
from . import apiblueprint
from .errors import forbidden

api = restful.Api(apiblueprint)

class GageList(restful.Resource):
	"""
	Lists all gages with basic info about each
	"""
	def get(self):
		output = dict()
		for gage in Gage.select():
			output[gage.id] = {'name': gage.name,
								'slug': gage.slug,
								'location': gage.location}
		return output

class GageAPI(restful.Resource):
	"""
	GET: More description about each gage, including sensors
	{name, slug, location, url(api), html(humans), sensors:{Sensor.id:{Sensor.stype, latest sample, latest sample time}}}
	
	POST: Update samples
		recieve: {'id': Gage.id, samples: {}
	"""
	def get(self, id=None):
		if id == None:
			return {'error': 'no gage id'}
		output = Gage.get(Gage.id == id)
		return {'name': output.name,
				'slug': output.slug,
				'location': output.location}
	
	def post(self, id=None):
		if id == None:
			return {'error': 'no gage id'}
		gage = Gage.get(Gage.id == id)
		



