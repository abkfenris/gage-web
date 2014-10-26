from flask import render_template, Response, make_response, url_for
from flask.ext.bootstrap import Bootstrap
import datetime
import random
import StringIO
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter, datestr2num, DayLocator

from . import main
from .. import db
#from auth import auth
from ..models import User, Region, River, Section, Gage, Sensor, Sample

#bootstrap = Bootstrap()

# Normal Pages

@main.route('/')
def indexpage():
	"""
	Index page
	"""
	#return render_template('index.html', Gage=Gage)
	return "Hello World!"
	
@main.route('/about/')
def aboutpage():
	"""
	About this site.
	"""
	return render_template('about.html', Gage=Gage)

@main.route('/gage/')
def gagespage():
	"""
	List of gages grouped by regions.
	"""
	return render_template('gages.html', Gage=Gage, Region=Region)
	
