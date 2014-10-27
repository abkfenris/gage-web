from flask import Blueprint

api = Blueprint('api', __name__)

# from . import correllations, gages, regions, rivers, samples, sections, sensors, users

from . import gages, sensors, samples, rivers, sections, regions

@api.route('/')
def indexpage():
	return 'Hello Api!'