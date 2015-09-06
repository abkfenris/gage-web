"""
Get flows from Army Corps of Engineers rivergages.mvr.usace.army.mil

Sensor.remote_id is the sid string in the url. e.g.:
For Canaserga Creek (http://rivergages.mvr.usace.army.mil/WaterControl/shefdata2.cfm?sid=DSVN6&d=1&dt=S)
the remote_id is DSVN6
"""
import arrow
from bs4 import BeautifulSoup
import requests

from .base import add_new_sample, RemoteGage


class Corps(RemoteGage):
    """
    Get flows from Army Corps of Engineers rivergages.mvr.usace.army.mil
    """
    URLBASE = 'http://rivergages.mvr.usace.army.mil/WaterControl/shefdata2.cfm'

    def soup(self, remote_id):
        """
        Return a beautiful soup object from rivergages.mvr.usace.army.mil
        """
        url = self.URLBASE + '?sid={}&d=1&dt=S'.format(remote_id)
        r = requests.get(url)
        return BeautifulSoup(r.text, 'html.parser')

    def dt_value(self, remote_id):
        """
        Return the most recent datetime and value
        """
        form = self.soup(remote_id).find('form', {'name': 'frm_daily'})
        table = form.findChild('table')
        children = table.findChildren('tr')[5].findChildren('td')
        dt = arrow.get(children[0].text, 'MM/DD/YYYY HH:mm').datetime
        value = float(children[1].text)
        return dt, value

    def get_sample(self, sensor_id):
        """
        Takes a sensor id, tries to get the latest sample from the Corps
        """
        sensor = self.sensor(sensor_id)
        dt, v = self.dt_value(sensor.remote_id)
        add_new_sample(sensor.id, dt, v)
