"""
Endpoints:
----------

- **/api/1.0/sensors/ - **GET** List all sensors
- **/api/1.0/sensors/<id> - **GET** Detailed information about sensor
- **/api/1.0/sensors/<id>/samples - **GET** Samples from sensor *id*
"""
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Gage, Sensor, Sample
from . import api

@api.route('/sensors/')
def get_sensors():
	"""
	List all sensors
	"""
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
	"""
	Detailed information about sensor *id*
	"""
	sensor = Sensor.query.get_or_404(id)
	return jsonify(sensor.to_long_json())

@api.route('/sensors/<int:id>/samples')
def get_sensor_samples(id):
	"""
	List samples for sensor *id*
	"""
	sensor = Sensor.query.get_or_404(id)
	page = request.args.get('page', 1, type=int)
	pagination = Sample.query.filter_by(sensor_id=id).paginate(page, per_page=current_app.config['API_GAGES_PER_PAGE'], error_out=False)
	samples = pagination.items
	prev = None
	#if pagination.has_prev:
	#	prev = url_for('.get_sensor_samples', page=page-1)
	next = None
	#if pagination.has_next:
	#	next = url_for('.get_sensor_samples', page=page+1)
	return jsonify({
		'sensor': sensor.to_json(),
		'samples': [sample.to_sensor_json() for sample in samples],
		'prev': prev,
		'next': next,
		'count': pagination.total,
	})