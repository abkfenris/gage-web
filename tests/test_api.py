from test_basics import BasicTestCase

class APITestCase(BasicTestCase):
	def test_api_root(self):
		rv = self.client.get('/api/1.0/')
		assert 'gages' in rv.data
		assert 'regions' in rv.data
		assert 'rivers' in rv.data
		assert 'samples' in rv.data
		assert 'sections' in rv.data
		assert 'sensors' in rv.data
	
	#def test_api_gages(self):
	#	rv = self.client.get('/api/1.0/gages/')