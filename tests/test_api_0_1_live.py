import requests

from .test_live import LiveServerBase


class API_0_1_Live(LiveServerBase):
    def test_server_is_up_and_running(self):
        """
        Server is running for Client 0.1 test (test_api_0_1_live.API_0_1_Live)
        """
        r = requests.get(self.get_server_url())
        self.assertEqual(r.status_code, 200)

    def test_api_base(self):
        """
        Base api endpoints (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url()))
        j = r.json()
        self.assertIn('gages', j)
        self.assertIn('sections', j)
        self.assertIn('regions', j)
        self.assertIn('rivers', j)
        self.assertIn('sensors', j)
        self.assertIn('samples', j)

    def test_api_gages(self):
        """
        Retrive gages from server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load gages from url specified in api base
        r = requests.get(r['gages']).json()
        self.assertIn('count', r)
        self.assertIn('gages', r)
        self.assertIn('next', r)
        self.assertIn('prev', r)
        for gage in r['gages']:
            if gage['name'] == 'Wild River at Gilead':
                testgage = gage
                break
        else:
            raise Exception('Wild River at Gilead gage not found')
        self.assertIn('name', testgage)
        self.assertIn('id', testgage)
        self.assertIn('location', testgage)
        self.assertIn('url', testgage)
        self.assertIn('html', testgage)
        self.assertIn('Wild River at Gilead', testgage['name'])

    def test_api_gage(self):
        """
        Retrieve a gage from the server (test_api_0_1.API_0_1_Live)
        """
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        r = requests.get(r['gages']).json()
        r = requests.get(r['gages'][0]['url']).json()
        self.assertIn('name', r)
        self.assertIn('id', r)
        self.assertIn('location', r)
        self.assertIn('name', r)
        self.assertIn('regions', r)
        self.assertIn('sensors', r)
        self.assertIn('html', r)
        self.assertIn('url', r)

    def test_api_regions(self):
        """
        Retrieve regions from server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load regions from url specified in api base
        r = requests.get(r['regions']).json()
        self.assertIn('count', r)
        self.assertIn('next', r)
        self.assertIn('prev', r)
        self.assertIn('regions', r)

    def test_api_region(self):
        """
        Retrieve region from server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load samples from url specified in api base
        r = requests.get(r['regions']).json()
        r = requests.get(r['regions'][0]['url']).json()
        self.assertIn('html', r)
        self.assertIn('id', r)
        self.assertIn('name', r)
        self.assertIn('url', r)
        self.assertIn('rivers', r)
        self.assertIn('sections', r)
        self.assertIn('gages', r)

    def test_api_rivers(self):
        """
        Retrieve rivers from server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load rivers from url specified in api base
        r = requests.get(r['rivers']).json()
        self.assertIn('count', r)
        self.assertIn('next', r)
        self.assertIn('prev', r)
        self.assertIn('rivers', r)

    def test_api_river(self):
        """
        Retrieve a river from server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load rivers from url specified in api base
        r = requests.get(r['rivers']).json()
        r = requests.get(r['rivers'][0]['url']).json()
        self.assertIn('html', r)
        self.assertIn('url', r)
        self.assertIn('sections', r)
        self.assertIn('gages', r)
        self.assertIn('regions', r)
        self.assertIn('tributaries', r)

    def test_api_samples(self):
        """
        Retrieve samples from server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load samples from url specified in api base
        r = requests.get(r['samples']).json()
        self.assertIn('count', r)
        self.assertIn('next', r)
        self.assertIn('prev', r)
        self.assertIn('samples', r)

    def test_api_sample(self):
        """
        Retrieve a sample from the server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load samples from url specified in api base
        r = requests.get(r['samples']).json()
        # load a sample
        r = requests.get(r['samples'][0]['url']).json()
        self.assertIn('datetime', r)
        self.assertIn('value', r)
        self.assertIn('id', r)
        self.assertIn('url', r)
        self.assertIn('sensor', r)

    def test_api_sections(self):
        """
        Retrieve sections from server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load sections from url specified in api base
        r = requests.get(r['sections']).json()
        self.assertIn('count', r)
        self.assertIn('next', r)
        self.assertIn('prev', r)
        self.assertIn('sections', r)
        section = r['sections'][0]
        self.assertIn('html', section)
        self.assertIn('url', section)
        self.assertIn('id', section)

    def test_api_sensors(self):
        """
        Retrive sensors from server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load sensors from url specified in api base
        r = requests.get(r['sensors']).json()
        self.assertIn('count', r)
        self.assertIn('sensors', r)
        self.assertIn('prev', r)
        self.assertIn('next', r)

    def test_api_sensor(self):
        """
        Retrive a sensor from server (test_api_0_1_live.API_0_1_Live)
        """
        # load api base
        r = requests.get('{server}/api/0.1/'.format(
            server=self.get_server_url())).json()
        # load sensors from url specified in api base
        r = requests.get(r['sensors']).json()
        r = requests.get(r['sensors'][0]['url']).json()
        self.assertIn('description', r)
        self.assertIn('started', r)
        self.assertIn('maximum', r)
        self.assertIn('recent_sample', r)
        self.assertIn('id', r)
        self.assertIn('type', r)
        self.assertIn('url', r)
        self.assertIn('minimum', r)
        self.assertIn('ended', r)
