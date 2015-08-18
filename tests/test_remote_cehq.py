import datetime

import vcr
import requests

from .test_basics import BasicTestCase

from app.remote import cehq

my_vcr = vcr.VCR(
    match_on = ['method']
)

class TestCEHQ(BasicTestCase):
    SITE_NUM = '050915'

    @my_vcr.use_cassette('tests/fixtures/cehq_get_response', ignore_localhost=True)
    def test_get_response(self):
        assert type(cehq.get_response(self.SITE_NUM)) == requests.Response

    @my_vcr.use_cassette('tests/fixtures/cehq_get_recent_flow', ignore_localhost=True)
    def test_get_recent_flow(self):
        flow = cehq.get_recent_flow(self.SITE_NUM)
        assert type(flow) == float
        assert flow >= 0
