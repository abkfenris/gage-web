"""
Retrieving samples from the USGS Instantaneous Values service
"""
import requests
import arrow
from flask import current_app

from app.models import Sensor
from .base import add_new_sample, RemoteGage

URLBASE = 'http://waterservices.usgs.gov/nwis/iv/?format=json,1.1'


class USGS(RemoteGage):
    URLBASE = 'http://waterservices.usgs.gov/nwis/iv/?format=json,1.1'

    @staticmethod
    def site_code(site_json):
        """
        From a USGS array item within ['value']['timeSeries']
        get the code back for the site
        """
        return str(site_json['sourceInfo']['siteCode'][0]['value'])

    @staticmethod
    def dt_value(site_json):
        """
        From a USGS array item within ['value']['timeSeries']
        return datetime, float value of sample
        """
        value = site_json['values'][0]['value'][0]
        dt = arrow.get(value['dateTime']).datetime
        v = float(value['value'])
        return dt, v

    def get_sample(self, sensor_id):
        """
        Takes a sensor id, tries to ge thte latest sample from the site
        """
        sensor = self.sensor(sensor_id)
        parameter = (sensor.remote_parameter or '00065')
        url = (self.URLBASE +
               '&sites=' + sensor.remote_id +
               '&parameterCD=' + parameter)
        site = requests.get(url).json()['value']['timeSeries'][0]
        dt, v = self.dt_value(site)
        add_new_sample(sensor.id, dt, v)

    def get_multiple_samples(self, sensor_ids):
        parameter = (self.sensor(sensor_ids[0]).remote_parameter or '00065')
        remote_sensors = Sensor.query.filter(Sensor.id.in_(sensor_ids))\
                                     .with_entities(Sensor.remote_id)\
                                     .all()
        remote_ids = [sensor[0] for sensor in remote_sensors]
        url = (URLBASE + '&sites=' + ','.join(remote_ids) +
               '&parameterCD=' + str(parameter))
        r = requests.get(url).json()
        for site in r['value']['timeSeries']:
            sc = self.site_code(site)
            dt, v = self.dt_value(site)
            sensor = Sensor.query.filter(Sensor.remote_id == sc).first()
            add_new_sample(sensor.id, dt, v)
