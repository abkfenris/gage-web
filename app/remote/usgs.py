import datetime

import requests
import arrow

from app.database import db
from app.models import Sensor, Sample

URLBASE = 'http://waterservices.usgs.gov/nwis/iv/?format=json,1.1'


def site_code(site_json):
    """
    From a USGS array item within ['value']['timeSeries']
    get the code back for the site
    """
    return str(site_json['sourceInfo']['siteCode'][0]['value'])

def usgs_dt_value(site_json):
    """
    From a USGS array item within ['value']['timeSeries']
    return datetime, float value of sample
    """
    value = site_json['values'][0]['value'][0]
    dt = arrow.get(value['dateTime']).datetime
    v = float(value['value'])
    return  dt, v


def get_multiple_level_sites(site_id_list):
    """
    Get the latest level from multiple usgs sensors
    """
    url = (URLBASE + '&sites=' + ','.join(site_id_list) +
           '&parameterCD=00065')
    r = requests.get(url).json()
    for site in r['value']['timeSeries']:
        sc = site_code(site)
        dt, v = usgs_dt_value(site)
        sensor = Sensor.query.filter(Sensor.remote_id == sc).first()
        sample = Sample.query.filter_by(sensor_id=sensor.id)\
                             .order_by(Sample.datetime.desc()).first()
        # only add a new sample if there is none, or there hasn't been one
        # in the last 10 min
        delta = datetime.datetime.now() - datetime.timedelta(minutes=10)
        if sample is None or sample.datetime < delta:
            sample = Sample(sensor_id=sensor.id,
                            value=v,
                            datetime=dt)
            db.session.add(sample)
            db.session.commit()


def get_multiple_level(sensor_id_list):
    """
    Get latest level from multiple usgs sensors
    """
    remote_sensors = Sensor.query.filter(Sensor.id.in_(sensor_id_list)).all()
    get_multiple_level_sites([sensor.remote_id for sensor in remote_sensors])


def get_samples(sensor,
                remote_id,
                period='P1D',
                startDT=None,
                endDT=None,
                parameter='00065'):

    # format url
    url = URLBASE + '&sites=' + remote_id
    if startDT is None or endDT is None:
        url = url + '&period=' + period
    else:
        url = url + '&startDT={start}&endDT={end}'.format(
                    start=startDT.strftime('%Y-%m-%dT%H:%MZ'),
                    end=endDT.strftime('%Y-%m-%dT%H:%MZ'))
    url = url + '&parameterCd=' + parameter

    # get url
    r = requests.get(url)

    # iterate over samples
    for sample in r.json()['value']['timeSeries'][0]['values'][0]['value']:
        time = arrow.get(sample['dateTime']).datetime
        # time = parser.parse(sample['dateTime']) # parsing time like
        # http://stackoverflow.com/questions/3305413/python-strptime-and-timezones
        sample = Sample(sensor_id=sensor.id,
                        value=float(sample['value']),
                        datetime=time)
        db.session.add(sample)
        db.session.commit()
