import datetime

import vcr

from .test_basics import BasicTestCase

from app.tasks import remote
from app.models import Sample

my_vcr = vcr.VCR(
    match_on = ['method', 'uri']
)


class TestRemoteline(BasicTestCase):
    SITE_NUM = 235127

    @my_vcr.use_cassette('tests/fixtures/fetch_remote_samples')
    def test_fetch_remote_samples(self):
        before = Sample.query.count()
        remote.fetch_remote_samples()
        after = Sample.query.count()
        assert after > before
