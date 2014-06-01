from flask import render_template, request, Response, make_response
import datetime
import random
import StringIO
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter, datestr2num

from app import app
# from auth import auth
from models import User, Sample, Gage

# Draw plots https://gist.github.com/wilsaj/862153

# test if matplotlib causes things to explode even when you have no samples
@app.route('/testplot/') 
@app.route('/testplot.png')
def plot():
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

@app.route('/gage/<int:id>/level/')
@app.route('/gage/<int:id>/level.png')
def gagelevelplot(id):
	fig = Figure()
	ax = fig.add_subplot(1, 1, 1)
	az = fig.add_subplot(1, 1, 1)
	x = []
	y = [] # need to figure out how to reverse axis
	for sample in Sample.select().where(Sample.gage == id).order_by(Sample.timestamp.desc()):
		x.append(sample.timestamp)
		y.append(sample.level)
	ax.plot(x, y, '-')
	fig.autofmt_xdate()
	ax.invert_yaxis() # remember we are looking at depth BELOW bridge
	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
	fig.suptitle('%s level in cm below gage' % Gage.get(Gage.id == id).name)
	canvas = FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	response = make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response

@app.route('/gage/<int:id>/battery/')
@app.route('/gage/<int:id>/battery.png')
def gagebatteryplot(id):
	fig = Figure()
	ax = fig.add_subplot(1, 1, 1)
	x = []
	y = []
	for sample in Sample.select().where(Sample.gage == id).order_by(Sample.timestamp.desc()):
		x.append(sample.timestamp)
		y.append(sample.battery)
	ax.plot(x, y, '-')
	fig.autofmt_xdate()
	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
	fig.suptitle('%s battery potential in Volts' % Gage.get(Gage.id == id).name)
	canvas = FigureCanvas(fig)
	png_output = StringIO.StringIO()
	canvas.print_png(png_output)
	response = make_response(png_output.getvalue())
	response.headers['Content-Type'] = 'image/png'
	return response