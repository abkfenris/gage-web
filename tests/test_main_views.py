from test_basics import BasicTestCase

class MainViewTestCase(BasicTestCase):
	def test_root(self):
		rv = self.client.get('/')
		assert 'hang around here' in rv.data
		
	def test_regions_view(self):
		rv = self.client.get('/regions/')
		assert 'Want more regions here?' in rv.data
	
	def test_rivers_view(self):
		rv = self.client.get('/rivers/')
		assert 'Want more rivers here?' in rv.data
	
	def test_sections_view(self):
		rv = self.client.get('/sections/')
		assert 'Want more sections here?' in rv.data
		
	def test_gages_view(self):
		rv = self.client.get('/gages/')
		assert 'Want more gages here' in rv.data
	
	# def test_map_view
	
	def test_about_view(self):
		rv = self.client.get('/about/')
		assert 'But Why' in rv.data
	
