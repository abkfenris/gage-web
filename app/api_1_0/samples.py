"""
Endpoints:
----------

- **/api/1.0/samples/ - **GET** List all samples
- **/api/1.0/samples/<id> - **GET** Detailed information about sample *id*
"""
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Gage, Sensor, Sample
from . import api

@api.route('/samples/')
def get_samples():
	"""
	List all samples
	"""
	page = request.args.get('page', 1, type=int)
	pagination = Sample.query.paginate(page, per_page=current_app.config['API_GAGES_PER_PAGE'], error_out=False)
	samples = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('.get_samples', page=page-1)
	next = None
	if pagination.has_next:
		next = url_for('.get_samples', page=page+1)
	return jsonify({
		'samples': [sample.to_json() for sample in samples],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})

@api.route('/samples/<int:id>')
def get_sample():
	"""
	Detailed information about sample *id*
	"""
	sample = Sample.query.get_or_404(id)
	return jsonify(sample.to_json())