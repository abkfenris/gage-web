import datetime

import vcr

from .test_basics import BasicTestCase

from app.remote import corps
from app.models import Sensor, Sample

my_vcr = vcr.VCR(

)


class TestCorps(BasicTestCase):
    SITES = ['DSVN6', 'SCNM5', 'SMW']
    Corps = corps.Corps()

    @my_vcr.use_cassette('tests/fixtures/corps_soup_dt_value')
    def test_soup_dt_value(self):
        for site_num in self.SITES:
            dt, value = self.Corps.dt_value(site_num)
            assert type(value) == float
            assert type(dt) == datetime.datetime

    @my_vcr.use_cassette('tests/fixtures/corps_get_sample')
    def test_get_sample(self):
        sensor = Sensor.query.filter(Sensor.remote_type == 'corps').first()
        before = Sample.query.count()
        self.Corps.get_sample(sensor.id)
        after = Sample.query.count()
        assert after > before
