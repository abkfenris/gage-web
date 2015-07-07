from .test_basics import BasicTestCase


class APITestCase(BasicTestCase):
    def test_api_root(self):
        rv = self.client.get('/api/0.1/')
        assert 'gages' in str(rv.data)
        assert 'regions' in str(rv.data)
        assert 'rivers' in str(rv.data)
        assert 'samples' in str(rv.data)
        assert 'sections' in str(rv.data)
        assert 'sensors' in str(rv.data)

    def test_api_gages(self):
        rv = self.client.get('/api/0.1/gages/')
        assert 'Wild River' in str(rv.data)

    def test_api_gage(self):
        rv = self.client.get('/api/0.1/gages/1')
        assert 'Wild River' in str(rv.data)

    def test_api_regions(self):
        rv = self.client.get('/api/0.1/regions/')
        assert 'Maine' in str(rv.data)

    def test_api_region(self):
        rv = self.client.get('/api/0.1/regions/1')
        assert 'Maine' in str(rv.data)

    def test_api_rivers(self):
        rv = self.client.get('/api/0.1/rivers/')
        assert 'Androscoggin' in str(rv.data)
        rv = self.client.get('/api/0.1/rivers/?page=2')
        assert 'Wild River' in str(rv.data)

    def test_api_river(self):
        rv = self.client.get('/api/0.1/rivers/1')
        assert 'Androscoggin' in str(rv.data)

    # def test_api_samples
    # def test_api_sample

    def test_api_sections(self):
        rv = self.client.get('/api/0.1/sections/')
        assert 'Wild River' in str(rv.data)

    def test_api_section(self):
        rv = self.client.get('/api/0.1/sections/1')
        assert 'Wild River' in str(rv.data)

    def test_api_sensors(self):
        rv = self.client.get('/api/0.1/sensors/')
        assert 'usgs-height' in str(rv.data)

    def test_api_sensor(self):
        rv = self.client.get('/api/0.1/sensors/1')
        assert 'Wild River' in str(rv.data)

    def test_api_sensor_samples(self):
        rv = self.client.get('/api/0/1/sensors/1/samples')
        assert 'Wild River' in str(rv.data)
