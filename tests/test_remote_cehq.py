import vcr
import requests

from .test_basics import BasicTestCase

from app.remote import cehq
from app.models import Sensor, Sample

my_vcr = vcr.VCR(
    match_on=['method']
)


class TestCEHQ(BasicTestCase):
    SITE_NUM = '050915'
    CEHQ = cehq.CEHQ()

    @my_vcr.use_cassette('tests/fixtures/cehq_get_response', ignore_localhost=True)
    def test_get_response(self):
        assert type(self.CEHQ.response(self.SITE_NUM)) == requests.Response

    @my_vcr.use_cassette('tests/fixtures/cehq_get_recent_flow', ignore_localhost=True)
    def test_get_recent_flow(self):
        flow = self.CEHQ.recent_flow(self.SITE_NUM)
        assert type(flow) == float
        assert flow >= 0

    @my_vcr.use_cassette('tests/fixtures/cehq_get_sample', ignore_localhost=True)
    def test_get_sample(self):
        sensor = Sensor.query.filter(Sensor.remote_type == 'cehq').first()
        before = Sample.query.count()
        self.CEHQ.get_sample(sensor.id)
        after = Sample.query.count()
        assert after > before
