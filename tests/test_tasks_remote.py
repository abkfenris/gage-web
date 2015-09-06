import time
from celerytest.testcase import CeleryTestCaseMixin, start_celery_worker
from celery import Celery
import vcr

from .test_basics import BasicTestCase

from celery_worker import app, celery
from app.tasks import remote
from app.models import Sample

my_vcr = vcr.VCR(
    match_on=['method', 'uri']
)

#app = Celery()
celery.conf.CELERY_ALWAYS_EAGER = True

class TestRemoteline(CeleryTestCaseMixin, BasicTestCase):
    SITE_NUM = 235127
    celery_app = celery
    #@my_vcr.use_cassette('tests/fixtures/fetch_remote_samples')

    def test_fetch_remote_samples(self, delay=False):
        before = Sample.query.count()
        remote.fetch_remote_samples()
        self.worker.idle.wait()
        time.sleep(20)
        after = Sample.query.count()
        assert after > before
