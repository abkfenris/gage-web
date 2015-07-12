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


def get_river(site_num, soup=None):
    """
    Return string with river name and location
    """
    if soup == None:
        soup = get_soup(site_num)
    river_strings = soup.body.findAll(text=re.compile(str(site_num)))
    return ' '.join(river_strings[0].split()[1:])


def get_cfs_strings(site_num, parameter='CFS', soup=None):
    """
    Return strings containing a cfs
    """
    if soup == None:
        soup = get_soup(site_num)
    p = re.compile('([\d.]+)+(?= {})'.format(parameter))
    return soup.body.findAll(text=p)


def get_cfs(site_num, parameter='CFS', soup=None):
    """
    Return float of first CFS found
    If given a parameter string, it will find that instead
    """
    if soup == None:
        cfs_strings = get_cfs_strings(site_num, parameter=parameter)
    else:
        cfs_strings = get_cfs_strings(site_num, parameter=parameter, soup=soup)
    p = re.compile('([\d.]+)+(?= {})'.format(parameter))
    result = p.search(cfs_strings[0])
    start, end = result.start(), result.end()
    return float(cfs_strings[0][start:end])


def get_samples(sensor,
                remote_id):
    from ..models import Sample

    # format url
