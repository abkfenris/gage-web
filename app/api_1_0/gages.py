"""
gages api imports api, app, db, auth, and models

Endpoints:
----------

- **/api/1.0/gages/** - **GET** List all gages
- **/api/1.0/gages/<id>** - **GET** Detailed information about gage number *id*
- **/api/1.0/gages/<id>/sample** - **POST** new sample data for gage *id*

"""

from flask import jsonify, request, g, abort, url_for, current_app
#from flask.ext import restful
from .. import db
from ..models import Gage
from . import api
#from .errors import forbidden

@api.route('/gages/')
def get_gages():
	"""**GET /api/1.0/gages/**
	
	List all gages
	"""
	page = request.args.get('page', 1, type=int)
	pagination = Gage.query.paginate(page, per_page=current_app.config['API_GAGES_PER_PAGE'], error_out=False)
	gages = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('.get_gages', page=page-1)
	next = None
	if pagination.has_next:
		next = url_for('.get_gages', page=page+1)
	return jsonify({
		'gages': [gage.to_json() for gage in gages],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})

@api.route('/gages/<int:id>')
def get_gage(id):
	"""**GET /api/1.0/gages/<id>**
	
	Detailed information about gage *id*
	"""
	gage = Gage.query.get_or_404(id)
	return jsonify(gage.to_long_json())

@api.route('/gages/<int:id>/sample', methods=['POST'])
def gage_new_samples(id):
	"""**POST /api/1.0/gages/<id>/samples**
	
	Submit new samples to gage *id*
	"""
	gage = Gage.query.get_or_404(id)
	req_json = request.get_json(force=True)
	print req_json['samples']
	for sample in req_json['samples']:
		print gage.new_sample(stype=sample['type'].lower(), value=sample['value'], sdatetime=sample['datetime'])
	return jsonify(request.json)