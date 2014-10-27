from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Region
from . import api

@api.route('/regions/')
def get_regions():
	page = request.args.get('page', 1, type=int)
	pagination = Region.query.paginate(page, per_page=current_app.config['API_GAGES_PER_PAGE'], error_out=False)
	regions = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('.get_regions', page=page-1)
	next = None
	if pagination.has_next:
		next = url_for('.get_regions', page=page+1)
	return jsonify({
		'sensors': [region.to_json() for region in regions],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})

@api.route('/regions/<int:id>')
def get_region(id):
	region = Region.query.get_or_404(id)
	return jsonify(region.to_long_json())