"""
Get flows from h2oline.com sites
"""

import re

from bs4 import BeautifulSoup
import requests

from ..database import db


def get_soup(site_num):
    """
    Return a beautiful soup object from h2oline
    """
    url = 'http://www.h2oline.com/default.aspx?pg=si&op={}'.format(site_num)
    r = requests.get(url)
    return BeautifulSoup(r.text, 'html.parser')


def get_river(site_num):
    """
    Return string with river name and location
    """
    soup = get_soup(site_num)
    river_strings = soup.body.findAll(text=re.compile(str(site_num)))
    return ' '.join(river_strings[0].split()[1:])


def get_cfs_strings(site_num, parameter='CFS'):
    """
    Return strings containing a cfs
    """
    soup = get_soup(site_num)
    p = re.compile('([\d.]+)+(?= {})'.format(parameter))
    return soup.body.findAll(text=p)


def get_cfs(site_num, parameter='CFS'):
    """
    Return float of first CFS found
    If given a parameter string, it will find that instead
    """
    cfs_strings = get_cfs_strings(site_num, parameter=parameter)
    p = re.compile('([\d.]+)+(?= {})'.format(parameter))
    result = p.search(cfs_strings[0])
    start, end = result.start(), result.end()
    return float(cfs_strings[0][start:end])


def get_samples(sensor,
                remote_id):
    from ..models import Sample

    # format url
