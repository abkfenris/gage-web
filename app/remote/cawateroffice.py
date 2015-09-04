import csv

import arrow
import requests

from .base import RemoteGage, add_new_sample


class WaterOffice(RemoteGage):
    """
    BC_07EA004
    """
    def get_from_wateroffice(self, remote_id):
        url = 'http://dd.weather.gc.ca/hydrometric/csv/BC/hourly/{}_hourly_hydrometric.csv'.format(remote_id)
        response = requests.get(url)
        riter = response.iter_lines()
        riter.next()
        reader = csv.reader(riter)
        lines = []
        for row in reader:
            lines.append(row)
        last = lines[-1]
        dt = arrow.get(last[1]).datetime
        level = last[2]
        discharge = last[6]
        return dt, level, discharge

    def get_sample(self, sensor_id):
        sensor = self.sensor(sensor_id)
        dt, level, discharge = self.get_from_wateroffice(sensor.remote_id)
        if sensor.remote_parameter == 'discharge':
            add_new_sample(sensor.id, dt, discharge)
        else:
            add_new_sample(sensor.id, dt, level)
