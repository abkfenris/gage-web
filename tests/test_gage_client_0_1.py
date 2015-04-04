import datetime
import requests

from .gage_client.gage_client import Client
from .test_live import LiveServerBase


class GageClient_0_1_Case(LiveServerBase):
    def test_server_is_up_and_running(self):
        r = requests.get(self.get_server_url())
        self.assertEqual(r.status_code, 200)

    def test_api_base(self):
        r = requests.get('{server}/api/0.1/'.format(server=self.get_server_url()))
        j = r.json()
        self.assertIn('gages', j)
        self.assertIn('sections', j)
        self.assertIn('regions', j)
        self.assertIn('rivers', j)
        self.assertIn('sensors', j)
        self.assertIn('samples', j)

    def test_api_gages(self):
        r = requests.get('{server}/api/0.1/gages'.format(server=self.get_server_url()))
        j = r.json()
        self.assertIn('count', j)
        for gage in j['gages']:
            if gage['name'] == 'Wild River at Gilead':
                testgage = gage
                break
        else:
            raise Exception('Wild River at Gilead gage not found')
        self.assertIn('Wild River at Gilead', testgage['name'])

    def test_gage_client(self):
        gage_client = Client('{server}/api/0.1/gages/1/sample'.format(server=self.get_server_url()), 1, 'password')
        dt = str(datetime.datetime.now())
        sensor = 'level'
        value = 4.2
        gage_client.reading(sensor, dt, value)
        self.assertEquals(len(gage_client.readings()), 1)
        gage_client.send_all()
        r = requests.get('{server}/api/0.1/gages/1'.format(server=self.get_server_url()))
        j = r.json()
        for sensor in j['sensors']:
            r = requests.get(sensor['url'])
            sj = r.json()
            if sj['recent_sample']['value'] == value:
                break
        else:
            raise Exception('Sample not found')
        sample = j['sensors'][1]['recent_sample']
        self.assertIn('url', sample)
        self.assertIn('id', sample)
        self.assertIn('value', sample)
        self.assertIn('datetime', sample)
        self.assertEquals(sample['value'], value)
