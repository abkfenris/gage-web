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
from auth import auth
from ..models import User, Region, River, Section, Gage, Sensor, Sample

bootstrap = Bootstrap(app)

# Normal Pages

@main.route('/')
def indexpage():
	"""
	Index page
	"""
	return render_template('index.html', Gage=Gage)
	
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
	
@main.route('/gage/<int:id>/')
def gagepage(id):
	"""
	Individual gage page.
	"""
	gage = Gage.get(Gage.id == id)
	return render_template('gage.html', gage=gage, id=id, Gage=Gage)

@main.route('/gage/gages.csv')
def gagecsv():
	"""
	.csv of all gages with shortDescription, latitude, and longitude. Largely for mapping
	"""
	output = 'id, name, shortDescription, latitude, longitude'
	for gage in Gage.select():
		output += '\n' + str(gage.id) + ', ' + gage.name + ', ' + gage.shortDescription + ', ' + str(gage.latitude) + ', ' + str(gage.longitude)
	response = make_response(output)
	response.headers['Content-Type'] = 'text/csv'
	return response

@main.route('/gage/gages.kml')
def gagekml():
	"""
	.kml of gages with url, level graph and shortDescription for mapping
	"""
	output = '<?xml version="1.0" encoding="UTF-8"?>'
	output += '\n<kml xmlns="http://www.opengis.net/kml/2.2">'
	output += '\n<Document>'
	for gage in Gage.select():
		output += '\n<Placemark>'
		output += '\n<name>' + gage.name + '</name>'
		output += '\n<description>'
		output += '\n<![CDATA['
		output += '\n<p>' + gage.shortDescription + '</p>'
		output += '\n<a href="' + url_for('gagepage', id=gage.id, _external=True ) + '">' + gage.name + '</a>'
		output += '\n<img src="' + url_for('gagelevelplot', id=gage.id, _external=True ) + '" width=300 class="img-responsive">'
		output += '\n]]>'
		output += '\n</description>'
		output += '\n<Point>'
		output += '\n<coordinates>' + str(gage.longitude) + ',' + str(gage.latitude) + ',0</coordinates>'
		output += '\n</Point>'
		output += '\n</Placemark>'
	output += '\n</Document>'
	output += '\n</kml>'
	response = make_response(output)
	response.headers['Content-Type'] = 'text/xml'
	return response

@main.route('/map/')
def mappage():
	"""
	Sometimes it's nicer to visually locate a gage, aka on a map.
	"""
	return render_template('map.html', Gage=Gage)

@main.route('/region/')
def regionspage():
	"""
	Once things get hopping view all gages by region.
	"""
	return render_template('regions.html', Region=Region, Gage=Gage)

@main.route('/region/<initial>/')
@main.route('/region/<int:id>/')
def regionpage(id=None, initial=None):
	"""
	View gages in a specific region, either by initials or region ID
	"""
	if initial is not None:
		region = Region.get(Region.initial == initial.upper())
		print initial
		print region.initial
		print region.name
	else:
		region = Region.get(Region.id == id)
	return render_template('region.html', region=region, Region=Region, Gage=Gage)


# Plots

# Draw plots https://gist.github.com/wilsaj/862153

# test if matplotlib causes things to explode even when you have no samples
@app.route('/testplot/') 
@app.route('/testplot.png')
def plot():
	"""
	Draw a generic plot to test that matplotlib actually works
	"""
	fig = Figure()
	ax = fig.add_subplot(1, 1, 1)
	x=[]
	y=[]
	now=datetime.datetime.now()
	delta=datetime.timedelta(days=1)
	for i in range(10):
		x.append(now)
		now+=delta
		y.append(random.randint(1, 1000))
	ax.plot_date(x, y, '-')
	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
	fig.autofmt_xdate()
	canvas=FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	response=make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response

@app.route('/gage/<int:id>/level.png')
@app.route('/gage/<int:id>/d<int:days>/level.png')
@app.route('/gage/<int:id>/<int:start>..<int:end>/level.png')
def gagelevelplot(id, days=7, start=None, end=None):
	"""
	Draw a plot for the gage.id level. If no d# or start/end days are specified draw a 7 day period
	"""
	if start == None and end == None:
		date_begin = datetime.datetime.utcnow() - datetime.timedelta(days=days)
		date_pad = date_begin - datetime.timedelta(days=1)
		date_end = datetime.datetime.utcnow()
	else:
		date_begin = datetime.datetime.strptime(str(start), '%Y%m%d')
		date_pad = date_begin - datetime.timedelta(days=1)
		date_end = datetime.datetime.strptime(str(end), '%Y%m%d')
		date_range = date_end-date_begin
		days = date_range.days
		print days
	fig = Figure()
	ax = fig.add_subplot(1, 1, 1)
	az = fig.add_subplot(1, 1, 1)
	x = []
	y = [] # need to figure out how to reverse axis
	for sample in Sample.select().where((Sample.gage == id) & (Sample.timestamp.between(date_pad, date_end)) ).order_by(Sample.timestamp.desc()):
		x.append(sample.timestamp)
		y.append(sample.level/100)
	ax.plot(x, y, '-')
	if days > 3:
		ax.xaxis.set_major_locator(DayLocator())
		ax.xaxis.set_major_formatter(DateFormatter('%b\n%d\n%Y'))
	else:
		fig.autofmt_xdate()
		ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
	ax.set_xlim(date_begin, date_end)
	if Gage.get(Gage.id == id).useLevels == True:
		ax.axhline(y=Gage.get(Gage.id == id).huge/100, color='#a94442')
		ax.axhline(y=Gage.get(Gage.id == id).high/100, color='#31708f')
		ax.axhline(y=Gage.get(Gage.id == id).medium/100, color='#3c763d')
		ax.axhline(y=Gage.get(Gage.id == id).low/100, color='#8a6d3b')
	else:
		pass
	fig.suptitle('%s river level in Meters' % Gage.get(Gage.id == id).name)
	canvas = FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	response = make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response


@app.route('/gage/<int:id>/battery.png')
@app.route('/gage/<int:id>/d<int:days>/battery.png')
@app.route('/gage/<int:id>/<int:start>..<int:end>/battery.png')
def gagebatteryplot(id, days=7, start=None, end=None):
	"""
	Draw a plot for the gage.id battery life. If no d# or start/end days are specified draw a 7 day period
	"""
	if start == None and end == None:
		date_begin = datetime.datetime.utcnow() - datetime.timedelta(days=days)
		date_pad = date_begin - datetime.timedelta(days=1)
		date_end = datetime.datetime.utcnow()
	else:
		date_begin = datetime.datetime.strptime(str(start), '%Y%m%d')
		date_pad = date_begin - datetime.timedelta(days=1)
		date_end = datetime.datetime.strptime(str(end), '%Y%m%d')
	fig = Figure()
	ax = fig.add_subplot(1, 1, 1)
	x = []
	y = []
	for sample in Sample.select().where((Sample.gage == id) & (Sample.timestamp.between(date_pad, date_end))).order_by(Sample.timestamp.desc()):
		x.append(sample.timestamp)
		y.append(sample.battery)
	ax.plot(x, y, '-')
	fig.autofmt_xdate()
	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
	ax.set_xlim(date_begin, date_end)
	fig.suptitle('%s battery potential in Volts' % Gage.get(Gage.id == id).name)
	canvas = FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	response = make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response