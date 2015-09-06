"""
Get flows from the Canadian Water Office

Sample.remote_id should be in the form of 2 Letter Province code, underscore,
then site number. e.g.:
The Cheticamp River (http://wateroffice.ec.gc.ca/report/report_e.html?type=realTime&stn=01FC002)
would be NS_01FC002
If discharge is prefered set the remote_parameter to discharge
"""
import csv

import arrow
import requests

from .base import RemoteGage, add_new_sample


class WaterOffice(RemoteGage):
    """
    BC_07EA004
    """
    def get_from_wateroffice(self, remote_id):
        province = remote_id.split('_')[0]
        url = 'http://dd.weather.gc.ca/hydrometric/csv/{}/hourly/{}_hourly_hydrometric.csv'.format(province, remote_id)
        response = requests.get(url)
        riter = response.iter_lines(decode_unicode=True)
        next(riter)
        reader = csv.reader(riter)
        lines = []
        for row in reader:
            lines.append(row)
        last = lines[-1]
        print(last)
        level = float(last[2])
        try:
            discharge = float(last[6])
        except ValueError:
            discharge = None
        dt = arrow.get(last[1]).datetime

        return dt, level, discharge

    def get_sample(self, sensor_id):
        sensor = self.sensor(sensor_id)
        dt, level, discharge = self.get_from_wateroffice(sensor.remote_id)
        if sensor.remote_parameter == 'discharge':
            add_new_sample(sensor.id, dt, discharge)
        else:
            add_new_sample(sensor.id, dt, level)
