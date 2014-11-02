"""
The main public routes to view the site
"""

from flask import render_template, Response, make_response, url_for, current_app

from . import main
from .. import db
from ..models import Gage, Region, Section, River

# Normal Pages

@main.route('/')
def indexpage():
	"""**/**
	
	Index page
	"""
	return render_template('index.html', Gage=Gage)
	#return current_app.config['SQLALCHEMY_DATABASE_URI']
	
@main.route('/about/')
def aboutpage():
	"""**/about/**
	
	About this site.
	"""
	return render_template('about.html', Gage=Gage)

@main.route('/gages/')
@main.route('/gage/')
def gagespage():
	"""**/gages/**
	
	List of gages currently not grouped by regions, or anything else for that matter.
	"""
	return render_template('gages.html', Gage=Gage)

@main.route('/gage/<int:id>/')
@main.route('/gage/<slug>/')
def gagepage(id=None, slug=None):
	"""**/gage/<slug>/**
	
	Individual gage page
	"""
	if slug is None:
		gage = Gage.query.get_or_404(id)
	else:
		gage = Gage.query.filter_by(slug=slug).first_or_404()
	return render_template('gage.html', Gage=Gage, gage=gage)

@main.route('/regions/')
@main.route('/region/')
def regionspage():
	"""**/regions/**
	
	List all regions
	"""
	return render_template('regions.html', Gage=Gage, Region=Region)

@main.route('/region/<int:id>/')
@main.route('/region/<slug>/')
def regionpage(id=None, slug=None):
	"""**/region/<slug>/**
	
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
							Section=Section,
							River=River)

@main.route('/sections/')
@main.route('/section/')
def sectionspage():
	"""**/sections/**
	
	List all sections
	"""
	return render_template('sections.html', Gage=Gage, Section=Section)

@main.route('/section/<int:id>/')
@main.route('/section/<slug>')
def sectionpage(id=None, slug=None):
	"""**/section/<slug>/**
	
	Individual section page
	"""
	if slug is None:
		section = Section.query.get_or_404(id)
	else:
		section = Section.query.filter_by(slug=slug).first_or_404()
	return render_template('section.html', Gage=Gage, Section=Section, section=section)

@main.route('/rivers/')
@main.route('/river/')
def riverspage():
	"""**/rivers/**
	
	List all rivers
	"""
	return render_template('rivers.html', Gage=Gage, River=River, Section=Section)

@main.route('/river/<int:id>/')
@main.route('/river/<slug>/')
def riverpage(id=None, slug=None):
	"""**/river/<slug>/**
	
	Individual river page
	"""
	if slug is None:
		river = River.query.get_or_404(id)
	else:
		river = River.query.filter_by(slug=slug).first_or_404()
	return render_template('river.html', 
							Gage=Gage, 
							River=River, 
							Section=Section, 
							river=river)