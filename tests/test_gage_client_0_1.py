import datetime
import requests

from .gage_client.gage_client import Client
from .test_live import LiveServerBase


class GageClient_0_1(LiveServerBase):

    def test_gage_client(self):
        """
        Sending a sample with Client_0_1 (test_gage_client_0_1.GageClient_0_1)
        """
        gage_client = Client('{server}/api/0.1/gages/1/sample'.format(
            server=self.get_server_url()), 1, 'password')
        dt = str(datetime.datetime.now())
        sensor = 'level'
        value = 4.2
        gage_client.reading(sensor, dt, value)
        self.assertEquals(len(gage_client.readings()), 1)
        gage_client.send_all()
        # check that the sample is avalaible on the gage page
        r = requests.get('{server}/api/0.1/gages/1'.format(
            server=self.get_server_url())).json()
        for sensor in r['sensors']:
            sj = requests.get(sensor['url']).json()
            if sj['recent_sample']['value'] == value:
                break
        else:
            raise Exception('Sample not found')
        sample = r['sensors'][1]['recent_sample']
        self.assertIn('url', sample)
        self.assertIn('id', sample)
        self.assertIn('value', sample)
        self.assertIn('datetime', sample)
        self.assertEquals(sample['value'], value)
        # check that the sample is avaliable on the samples page
        r = requests.get('{server}/api/0.1/samples/'.format(
            server=self.get_server_url())).json()
        self.assertIn('count', r)
        self.assertIn('prev', r)
        self.assertIn('samples', r)
        self.assertIn('next', r)
        # check that sample from server setup is present
        self.assertEquals(5.8, r['samples'][0]['value'])
        # check for a sample from client has been submitted
        r = requests.get(r['next']).json()
        self.assertEquals(4.2, r['samples'][0]['value'])
        # get sample info
        r = requests.get(r['samples'][0]['url']).json()
        self.assertIn('url', r)
        self.assertIn('id', r)
        self.assertIn('value', r)
        self.assertIn('datetime', r)
        self.assertIn('sensor', r)
        s = r['sensor']
        self.assertEquals('level', s['type'])
