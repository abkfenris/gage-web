"""

Endpoints:
----------

- **/api/1.0/regions/<id>** - **GET** Detailed information about region *id*
- **/api/1.0/rivers/ - **GET** List all rivers

"""
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import River
from . import api

@api.route('/rivers/')
def get_rivers():
	"""
	List all rivers
	"""
	page = request.args.get('page', 1, type=int)
	pagination = River.query.paginate(page, per_page=current_app.config['API_GAGES_PER_PAGE'], error_out=False)
	rivers = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('.get_sensors', page=page-1)
	next = None
	if pagination.has_next:
		next = url_for('.get_sensors', page=page+1)
	return jsonify({
		'rivers': [river.to_json() for river in rivers],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})

@api.route('/rivers/<int:id>')
def get_river(id):
	"""
	Detailed information about river *id*
	"""
	river = River.query.get_or_404(id)
	return jsonify(river.to_long_json())