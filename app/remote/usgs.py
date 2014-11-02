import requests
import datetime
from dateutil import parser
from .. import db

def get_samples(sensor, remote_id, period='P1D', startDT=None, endDT=None, parameter='00065'):
	from ..models import Sample, Sensor
	
	# format url
	urlbase = 'http://waterservices.usgs.gov/nwis/iv/?format=json,1.1'
	url = urlbase + '&sites=' + remote_id
	if startDT is None or endDT is None:
	    url = url + '&period=' + period
	else:
	    url = url + '&startDT=' + startDT.strftime('%Y-%m-%dT%H:%MZ') + '&endDT=' + endDT.strftime('%Y-%m-%dT%H:%MZ')
	url = url + '&parameterCd=' + parameter
	
	# get url
	r = requests.get(url)
	
	# iterate over samples
	for sample in r.json()['value']['timeSeries'][0]['values'][0]['value']:
		time = parser.parse(sample['dateTime']) # parsing time like http://stackoverflow.com/questions/3305413/python-strptime-and-timezones
		sample = Sample(sensor_id=sensor.id, value=float(sample['value']), datetime=time )
		db.session.add(sample)
		db.session.commit()