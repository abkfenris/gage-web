from test_basics import BasicTestCase


class APITestCase(BasicTestCase):
    def test_api_root(self):
        rv = self.client.get('/api/0.1/')
        assert 'gages' in rv.data
        assert 'regions' in rv.data
        assert 'rivers' in rv.data
        assert 'samples' in rv.data
        assert 'sections' in rv.data
        assert 'sensors' in rv.data

    def test_api_gages(self):
        rv = self.client.get('/api/0.1/gages/')
        assert 'Wild River' in rv.data

    def test_api_gage(self):
        rv = self.client.get('/api/0.1/gages/1')
        assert 'Wild River' in rv.data

    def test_api_regions(self):
        rv = self.client.get('/api/0.1/regions/')
        assert 'Maine' in rv.data

    def test_api_region(self):
        rv = self.client.get('/api/0.1/regions/1')
        assert 'Maine' in rv.data

    def test_api_rivers(self):
        rv = self.client.get('/api/0.1/rivers/')
        assert 'Androscoggin' in rv.data
        assert 'Wild River' in rv.data

    def test_api_river(self):
        rv = self.client.get('/api/0.1/rivers/1')
        assert 'Androscoggin' in rv.data

    # def test_api_samples
    # def test_api_sample

    def test_api_sections(self):
        rv = self.client.get('/api/0.1/sections/')
        assert 'Wild River' in rv.data

    def test_api_section(self):
        rv = self.client.get('/api/0.1/sections/1')
        assert 'Wild River' in rv.data

    def test_api_sensors(self):
        rv = self.client.get('/api/0.1/sensors/')
        assert 'usgs-height' in rv.data

    def test_api_sensor(self):
        rv = self.client.get('/api/0.1/sensors/1')
        assert 'Wild River' in rv.data

    def test_api_sensor_samples(self):
        rv = self.client.get('/api/0/1/sensors/1/samples')
        assert 'Wild River' in rv.data
