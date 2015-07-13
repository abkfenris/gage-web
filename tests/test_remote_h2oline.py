import datetime

import vcr

from .test_basics import BasicTestCase

from app.remote import h2oline

my_vcr = vcr.VCR(
    match_on = ['method']
)


class TestH2Oline(BasicTestCase):
    SITE_NUM = 235127

    @my_vcr.use_cassette('tests/fixtures/h2oline_get_river', ignore_localhost=True)
    def test_get_river(self):
        assert h2oline.get_river(self.SITE_NUM) == 'RAPID RIVER MIDDLE DAM ON RICHARDSON LAKE, ME'

    @my_vcr.use_cassette('tests/fixtures/h2oline_get_cfs', ignore_localhost=True)
    def test_get_cfs(self):
        assert type(h2oline.get_cfs(self.SITE_NUM)) == float

    @my_vcr.use_cassette('tests/fixtures/h2oline_soup_get_river_cfs')
    def test_soup_get_river_cfs(self):
        soup = h2oline.get_soup(self.SITE_NUM)
        assert h2oline.get_river(self.SITE_NUM, soup=soup) == 'RAPID RIVER MIDDLE DAM ON RICHARDSON LAKE, ME'
        assert type(h2oline.get_cfs(self.SITE_NUM, soup=soup)) == float

    @my_vcr.use_cassette('tests/fixtures/h2oline_get_dt_cfs')
    def test_get_dt_cfs(self):
        dt, value = h2oline.get_dt_cfs(self.SITE_NUM)
        assert type(dt) == datetime.datetime
        assert type(value) == float
