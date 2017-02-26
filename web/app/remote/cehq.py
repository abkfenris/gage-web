"""
Get flows from the Quebec CEHQ site
Sensor.remote_id is the Numero de la station e.g.: 050915 for the Nelson (http://www.cehq.gouv.qc.ca/suivihydro/graphique.asp?NoStation=050915)
"""
import datetime
import logging
import requests

from app.models import Sensor
from .base import add_new_sample, RemoteGage

logger = logging.getLogger(__name__)


def digit_or_period(c):
    """Returns True if the character c given is a string or a period"""
    return str.isdigit(c) or c is '.'


class CEHQ(RemoteGage):
    URLBASE = 'http://www.cehq.gouv.qc.ca/suivihydro/fichier_donnees.asp'

    def response(self, site_num):
        """
        Retrieve a requests.Response object for the plain text representation
        of a Quebec CEHQ gage
        """
        url = (self.URLBASE +
               '?NoStation=' + str(site_num))
        return requests.get(url)

    def recent_flow(self, site_num):
        r = self.response(site_num)
        line = r.text.splitlines()[2]
        number = line.split('\t')[2].replace(',', '.')
        return float(''.join(list(filter(digit_or_period, number))))

    def get_sample(self, sensor_id):
        sensor = self.sensor(sensor_id)
        v = self.recent_flow(sensor.remote_id)
        dt = datetime.datetime.now()
        add_new_sample(sensor.id, dt, v)
