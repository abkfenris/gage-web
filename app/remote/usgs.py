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


def add_new_sample(sensor_id, dt, svalue, deltaminutes=30):
    """
    Adds a new sample with an associacted remote sensor
    if there hasn't been a sample recorded within the last deltaminutes
    (default is 10).
    Arguments:
        sensor_id (int): Primary key for sensor
        dt (datetime): Datetime of sample
        svalue (float): Value of sample
    """
    delta = datetime.datetime.now() - datetime.timedelta(minutes=deltaminutes)
    sample = Sample.query.filter_by(sensor_id=sensor_id)\
                         .order_by(Sample.datetime.desc()).first()
    if sample is None or (sample.datetime < delta and (sample.datetime != dt.replace(tzinfo=None))):
        new_sample = Sample(sensor_id=sensor_id,
                            value=svalue,
                            datetime=dt)
        db.session.add(new_sample)
        db.session.commit()


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
        add_new_sample(sensor.id, dt, v)


def get_multiple_level(sensor_id_list):
    """
    Get latest level from multiple usgs sensors
    """
    remote_sensors = Sensor.query.filter(Sensor.id.in_(sensor_id_list)).all()
    get_multiple_level_sites([sensor.remote_id for sensor in remote_sensors])


def get_other_sample(sensor_id):
    sensor = Sensor.query.filter(Sensor.id == sensor_id).first()
    url = (URLBASE +
           '&sites=' + sensor.remote_id +
           '&parameterCD=' + sensor.remote_parameter)
    site = requests.get(url).json()['value']['timeSeries'][0]
    dt, v = usgs_dt_value(site)
    add_new_sample(sensor.id, dt, v)


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
