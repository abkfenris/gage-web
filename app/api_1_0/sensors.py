from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Gage, Sensor, Sample
from . import api

@api.route('/sensors/')
def get_sensors():
	page = request.args.get('page', 1, type=int)
	pagination = Sensor.query.paginate(page, per_page=current_app.config['API_GAGES_PER_PAGE'], error_out=False)
	sensors = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('.get_sensors', page=page-1)
	next = None
	if pagination.has_next:
		next = url_for('.get_sensors', page=page+1)
	return jsonify({
		'sensors': [sensor.to_json() for sensor in sensors],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})

@api.route('/sensors/<int:id>')
def get_sensor(id):
	sensor = Sensor.query.get_or_404(id)
	return jsonify(sensor.to_long_json())