from test_basics import BasicTestCase

class APITestCase(BasicTestCase):
	def test_api_root(self):
		rv = self.client.get('/api/1.0/')
		assert 'sections' in rv.data