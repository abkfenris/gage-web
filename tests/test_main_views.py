import vcr

from .test_basics import BasicTestCase

my_vcr = vcr.VCR(
    match_on = ['method']
)


class MainViews(BasicTestCase):
    def test_root(self):
        """
        View the index page (test_main_views.MainViews)
        """
        rv = self.client.get('/')
        assert 'hang around here' in str(rv.data)

    def test_regions_view(self):
        """
        View the region page (test_main_views.MainViews)
        """
        rv = self.client.get('/regions/')
        assert 'Want more regions here?' in str(rv.data)

    def test_region_view(self):
        """
        View a single region (test_main_views.MainViews)
        """
        rv = self.client.get('/region/maine/')
        assert 'Maine' in str(rv.data)
        rv = self.client.get('/region/1/')
        assert 'Maine' in str(rv.data)

    def test_rivers_view(self):
        """
        View the rivers page (test_main_views.MainViews)
        """
        rv = self.client.get('/rivers/')
        assert 'Want more rivers here?' in str(rv.data)

    def test_river_rivew(self):
        """
        View a single river page (test_main_views.MainViews)
        """
        rv = self.client.get('/river/androscoggin/')
        assert 'Androscoggin' in str(rv.data)
        rv = self.client.get('/river/1/')
        assert 'Androscoggin' in str(rv.data)

    def test_sections_view(self):
        """
        View the sections page (test_main_views.MainViews)
        """
        rv = self.client.get('/sections/')
        assert 'Wild River' in str(rv.data)
        assert 'Want more sections here?' in str(rv.data)

    def test_section_view(self):
        """
        View a single section page (test_main_views.MainViews)
        """
        rv = self.client.get('/section/wild-river/')
        assert 'Wild River' in str(rv.data)
        rv = self.client.get('/section/1/')
        assert 'Wild River' in str(rv.data)

    def test_gages_view(self):
        """
        View the gages page (test_main_views.MainViews)
        """
        rv = self.client.get('/gages/')
        assert 'Want more gages here' in str(rv.data)
        assert 'Wild River' in str(rv.data)

    @my_vcr.use_cassette('tests/fixtures/main_test_gage_view', ignore_localhost=True)
    def test_gage_view(self):
        """
        View a single gage page (test_main_views.MainViews)
        """
        rv = self.client.get('/gage/wild-river-gilead/')
        assert 'Wild River' in str(rv.data)
        assert 'Gage Height' in str(rv.data)
        rv = self.client.get('/gage/1/')
        assert 'Wild River' in str(rv.data)
        assert 'Gage Height' in str(rv.data)

    # def test_map_view
    def test_about_view(self):
        """
        View the about page (test_main_views.MainViews)
        """
        rv = self.client.get('/about/')
        assert 'But Why' in str(rv.data)

    def test_505_view(self):
        """
        Test the 404 error page (test_main_views.MainViews)
        """
        rv = self.client.get('/404')
        assert 'Boof Stroke Not Found' in str(rv.data)
