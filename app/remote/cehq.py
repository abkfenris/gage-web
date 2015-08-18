"""
Get flows from the Quebec CEHQ site
"""
import datetime
import logging
import requests

from app.models import Sensor
from . import add_new_sample

logger = logging.getLogger(__name__)


def get_response(site_num):
    """
    Retrieve a requests.Response object for the plain text representation of a
    Quebec CEHQ gage
    """
    return requests.get('http://www.cehq.gouv.qc.ca/suivihydro/fichier_donnees.asp?NoStation={}'.format(site_num))


def get_recent_flow(site_num):
    r = get_response(site_num)
    line = r.text.splitlines()[2]
    return float(line.split('\t')[2].replace(',', '.'))


def get_sample(sensor_id):
    """
    Takes a sensor id, tries to retrieve the latest sample from the site
    """
    sensor = Sensor.query.filter(Sensor.id == sensor_id).first()
    v = get_recent_flow(sensor.remote_id)
    dt = datetime.datetime.now()
    add_new_sample(sensor.id, dt, v)
