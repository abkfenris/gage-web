from test_basics import BasicTestCase


class MainViews(BasicTestCase):
    def test_root(self):
        """
        View the index page (test_main_views.MainViews)
        """
        rv = self.client.get('/')
        assert 'hang around here' in rv.data

    def test_regions_view(self):
        """
        View the region page (test_main_views.MainViews)
        """
        rv = self.client.get('/regions/')
        assert 'Want more regions here?' in rv.data

    def test_region_view(self):
        """
        View a single region (test_main_views.MainViews)
        """
        rv = self.client.get('/region/maine/')
        assert 'Maine' in rv.data
        rv = self.client.get('/region/1/')
        assert 'Maine' in rv.data

    def test_rivers_view(self):
        """
        View the rivers page (test_main_views.MainViews)
        """
        rv = self.client.get('/rivers/')
        assert 'Want more rivers here?' in rv.data

    def test_river_rivew(self):
        """
        View a single river page (test_main_views.MainViews)
        """
        rv = self.client.get('/river/androscoggin/')
        assert 'Androscoggin' in rv.data
        rv = self.client.get('/river/1/')
        assert 'Androscoggin' in rv.data

    def test_sections_view(self):
        """
        View the sections page (test_main_views.MainViews)
        """
        rv = self.client.get('/sections/')
        assert 'Wild River' in rv.data
        assert 'Want more sections here?' in rv.data

    def test_section_view(self):
        """
        View a single section page (test_main_views.MainViews)
        """
        rv = self.client.get('/section/wild-river/')
        assert 'Wild River' in rv.data
        rv = self.client.get('/section/1/')
        assert 'Wild River' in rv.data

    def test_gages_view(self):
        """
        View the gages page (test_main_views.MainViews)
        """
        rv = self.client.get('/gages/')
        assert 'Want more gages here' in rv.data
        assert 'Wild River' in rv.data

    def test_gage_view(self):
        """
        View a single gage page (test_main_views.MainViews)
        """
        rv = self.client.get('/gage/wild-river-gilead/')
        assert 'Wild River' in rv.data
        assert 'Gage Height' in rv.data
        rv = self.client.get('/gage/1/')
        assert 'Wild River' in rv.data
        assert 'Gage Height' in rv.data

    # def test_map_view
    def test_about_view(self):
        """
        View the about page (test_main_views.MainViews)
        """
        rv = self.client.get('/about/')
        assert 'But Why' in rv.data
