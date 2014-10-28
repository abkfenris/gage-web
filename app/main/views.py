from flask import render_template, Response, make_response, url_for, current_app
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
from ..models import Gage, Region, Section

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
@main.route('/gage/<slug>/')
def gagepage(id=None, slug=None):
	"""
	Individual gage page
	"""
	if slug is None:
		gage = Gage.query.get_or_404(id)
	else:
		gage = Gage.query.filter_by(slug=slug).first_or_404()
	return render_template('gage.html', Gage=Gage, gage=gage)

@main.route('/region/')
def regionspage():
	"""
	List all regions
	"""
	return render_template('regions.html', Gage=Gage, Region=Region)

@main.route('/region/<int:id>/')
@main.route('/region/<slug>/')
def regionpage(id=None, slug=None):
	"""
	Individual region page
	"""
	if slug is None:
		region = Region.query.get_or_404(id)
	else:
		region = Region.query.filter_by(slug=slug).first_or_404()
	return render_template('region.html', 
							Gage=Gage, 
							Region=Region, 
							region=region, 
							Section=Section)

@main.route('/section/')
def sectionspage():
	"""
	List all sections
	"""
	return render_template('sections.html', Gage=Gage, Section=Section)

@main.route('/section/<int:id>/')
@main.route('/section/<slug>')
def sectionpage(id=None, slug=None):
	if slug is None:
		section = Section.query.get_or_404(id)
	else:
		section = Section.query.filter_by(slug=slug).first_or_404()
	return render_template('section.html', Gage=Gage, Section=Section, section=section)