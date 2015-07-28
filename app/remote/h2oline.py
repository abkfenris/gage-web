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
from . import add_new_sample

logger = logging.getLogger(__name__)

def get_soup(site_num):
    """
    Return a beautiful soup object from h2oline
    """
    url = 'http://www.h2oline.com/default.aspx?pg=si&op={}'.format(site_num)
    r = requests.get(url)
    return BeautifulSoup(r.text, 'html.parser')


def get_river(site_num, soup=None):
    """
    Return string with river name and location
    """
    if soup is None:
        soup = get_soup(site_num)
    river_strings = soup.body.findAll(text=re.compile(str(site_num)))
    return ' '.join(river_strings[0].split()[1:])


def get_cfs_strings(site_num, parameter='CFS', soup=None):
    """
    Return strings containing a cfs
    """
    if soup is None:
        soup = get_soup(site_num)
    p = re.compile('([\d.]+)+(?= {})'.format(parameter))
    return soup.body.findAll(text=p)


def get_parameter_start_end(string, parameter):
    """
    Return the start and end of the parameter in the string
    """
    p = re.compile('([\d.]+)+(?= {})'.format(parameter))
    result = p.search(string)
    return result.start(), result.end()


def get_cfs(site_num, parameter='CFS', soup=None):
    """
    Return float of first CFS found
    If given a parameter string, it will find that instead
    """
    if soup is None:
        cfs_strings = get_cfs_strings(site_num, parameter=parameter)
    else:
        cfs_strings = get_cfs_strings(site_num, parameter=parameter, soup=soup)
    start, end = get_parameter_start_end(cfs_strings[0], parameter)
    return float(cfs_strings[0][start:end])


def natural_to_datetime(timestring):
    """
    Takes a natural sentance
    Returns a datetime instance
    """
    cal = parsedatetime.Calendar()
    t = cal.parse(timestring)
    dt = datetime.datetime(*t[0][0:7])
    # If the datetime parsed is not within 7 days of today just use right now
    if (dt > (datetime.datetime.now() - datetime.timedelta(days=1))):
        message = 'Found {0}'.format(str(dt))
        print(message)
        logger.info(message)
        return dt
    else:
        message = ('Unable to find a valid date within "{0}". Found {1} instead'
                   .format(timestring, str(dt)))
        print(message)
        logger.warning(message)
        return datetime.datetime.now()


def get_dt_cfs(site_num, parameter='CFS', soup=None):
    """
    Returns datetime and float of first CFS (or other parameter) found
    """
    if soup is None:
        cfs_strings = get_cfs_strings(site_num, parameter=parameter)
    else:
        cfs_strings = get_cfs_strings(site_num, parameter=parameter, soup=soup)
    start, end = get_parameter_start_end(cfs_strings[0], parameter)
    dt = datetime.datetime.now()
    return dt, float(cfs_strings[0][start:end])


def get_sample(sensor_id):
    """
    Takes a sensor id, tries to get the latest sample from the site
    """
    sensor = Sensor.query.filter(Sensor.id == sensor_id).first()
    if sensor.remote_parameter is None:
        dt, v = get_dt_cfs(sensor.remote_id)
    else:
        dt, v = get_dt_cfs(sensor.remote_id, parameter=sensor.remote_parameter)
    add_new_sample(sensor.id, dt, v)
