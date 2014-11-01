from flask import Blueprint, jsonify, url_for

api = Blueprint('api', __name__)

# from . import correllations, gages, regions, rivers, samples, sections, sensors, users

from . import gages, sensors, samples, rivers, sections, regions

@api.route('/')
def indexpage():
	return jsonify({
		'gages': url_for('api.get_gages', _external=True),
		'sensors': url_for('api.get_sensors', _external=True),
		'samples': url_for('api.get_samples', _external=True),
		'rivers': url_for('api.get_rivers', _external=True),
		'sections': url_for('api.get_sections', _external=True),
		'regions': url_for('api.get_regions', _external=True),
	})