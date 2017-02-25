import os

import vcr

from .test_basics import BasicTestCase

os.environ['FLASK_CONFIG'] = 'testing'

from app.database import db
from app.tasks import remote
from app.models import Sample, Sensor

my_vcr = vcr.VCR(
    match_on=['method', 'uri']
)


class TestRemoteline(BasicTestCase):
    SITE_NUM = 235127

    @my_vcr.use_cassette('tests/fixtures/tasks_fetch_remote_samples')
    def test_fetch_remote_samples(self, delay=False):
        before = Sample.query.count()
        remote.fetch_remote_samples()
        after = Sample.query.count()
        assert after > before

    @my_vcr.use_cassette('tests/fixtures/tasks_fetch_remote_samples_error')
    def test_fetch_remote_samples_error(self, delay=False):
        random_stage = Sensor(name='Canaseraga Creek',
                              stype='canaseraga-stage',
                              local=False, remote_type='random',
                              remote_id='DSVN6')
        db.session.add(random_stage)
        before = Sample.query.count()
        remote.fetch_remote_samples()
        after = Sample.query.count()
        assert after > before
