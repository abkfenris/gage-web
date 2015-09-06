"""
Retrieving samples from the USGS Instantaneous Values service
"""
import requests
import arrow

from app.models import Sensor
from .base import add_new_sample, RemoteGage

URLBASE = 'http://waterservices.usgs.gov/nwis/iv/?format=json,1.1'


class USGS(RemoteGage):
    URLBASE = 'http://waterservices.usgs.gov/nwis/iv/?format=json,1.1'

    def site_code(selt, site_json):
        """
        From a USGS array item within ['value']['timeSeries']
        get the code back for the site
        """
        return str(site_json['sourceInfo']['siteCode'][0]['value'])

    def dt_value(self, site_json):
        """
        From a USGS array item within ['value']['timeSeries']
        return datetime, float value of sample
        """
        value = site_json['values'][0]['value'][0]
        dt = arrow.get(value['dateTime']).datetime
        v = float(value['value'])
        return dt, v

usgs = USGS()


def get_multiple_level_sites(site_id_list):
    """
    Get the latest level from multiple usgs sensors
    """
    url = (URLBASE + '&sites=' + ','.join(site_id_list) +
           '&parameterCD=00065')
    r = requests.get(url).json()
    for site in r['value']['timeSeries']:
        sc = usgs.site_code(site)
        dt, v = usgs.dt_value(site)
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
    dt, v = usgs.dt_value(site)
    add_new_sample(sensor.id, dt, v)
