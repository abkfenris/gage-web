"""
Get flows (and other parameters) from h2oline.com sites
"""
import datetime
import logging
import re

from bs4 import BeautifulSoup
import requests
import parsedatetime

from app.models import Sensor
from .base import add_new_sample, RemoteGage

logger = logging.getLogger(__name__)


class H2Oline(RemoteGage):
    @staticmethod
    def soup(remote_id):
        """
        Return a beautiful soup object from h2oline
        """
        url = 'http://www.h2oline.com/default.aspx?pg=si&op={}'.format(remote_id)
        r = requests.get(url)
        return BeautifulSoup(r.text, 'html.parser')

    def river(self, remote_id, soup=None):
        """
        Return string with river name and location
        """
        if soup is None:
            soup = self.soup(remote_id)
        river_strings = soup.body.findAll(text=re.compile(str(remote_id)))
        return ' '.join(river_strings[0].split()[1:])

    def value_strings(self, remote_id, parameter='CFS', soup=None):
        """
        Return strings containing specified parameter
        """
        if soup is None:
            soup = self.soup(remote_id)
        p = re.compile('([\d.]+)+(?= {})'.format(parameter))
        return soup.body.findAll(text=p)

    @staticmethod
    def start_end(string, parameter):
        """
        Return the start and end of the parameter in the string
        """
        p = re.compile('([\d.]+)+(?= {})'.format(parameter))
        result = p.search(string)
        return result.start(), result.end()

    def value(self, remote_id, parameter='CFS', soup=None):
        """
        Return float of first CFS found
        If given a parameter string, it will find that instead
        """
        if soup is None:
            cfs_strings = self.value_strings(remote_id, parameter=parameter)
        else:
            cfs_strings = self.value_strings(remote_id, parameter=parameter, soup=soup)
        start, end = self.start_end(cfs_strings[0], parameter)
        return float(cfs_strings[0][start:end])


    def dt_value(self, remote_id, parameter='CFS', soup=None):
        """
        Returns datetime and float of first CFS (or other parameter) found
        """
        strings = self.value_strings(remote_id,
                                     parameter=parameter,
                                     soup=soup)
        start, end = self.start_end(strings[0], parameter)
        dt = datetime.datetime.now()
        return dt, float(strings[0][start:end])

    def get_sample(self, sensor_id):
        """
        Takes a sensor id, tries to get the latest sample from the site
        """
        sensor = self.sensor(sensor_id)
        if sensor.remote_parameter is None:
            dt, v = self.dt_value(sensor.remote_id)
        else:
            dt, v = self.dt_value(sensor.remote_id,
                                  paramter=sensor.remote_parameter)
        add_new_sample(sensor.id, dt, v)
