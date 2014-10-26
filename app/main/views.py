from flask import render_template, Response, make_response, url_for, current_app
#from flask.ext.bootstrap import Bootstrap
#import datetime
#import random
#import StringIO
#import matplotlib
#matplotlib.use('Agg')
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure
#from matplotlib.dates import DateFormatter, datestr2num, DayLocator

from . import main
from .. import db
#from auth import auth
#from ..models import User, Region, River, Section, Gage, Sensor, Sample
from ..models import Gage, Region

#bootstrap = Bootstrap()

# Normal Pages

@main.route('/')
def indexpage():
	"""
	Index page
	"""
	return render_template('index.html', Gage=Gage)
	#return current_app.config['SQLALCHEMY_DATABASE_URI']
	
@main.route('/about/')
def aboutpage():
	"""
	About this site.
	"""
	return render_template('about.html', Gage=Gage)

@main.route('/gage/')
def gagespage():
	"""
	List of gages currently not grouped by regions, or anything else for that matter.
	"""
	return render_template('gages.html', Gage=Gage)

@main.route('/gage/<int:id>/')
@main.route('/gage/<int:id>')
def gagepage(id):
	"""
	Individual gage page
	"""
	gage = Gage.query.get(id)
	return render_template('gage.html', Gage=Gage, gage=gage)

@main.route('/region/')
def regionspage():
	"""
	List all regions
	"""
	return render_template('regions.html', Gage=Gage, Region=Region)