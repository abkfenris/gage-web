import vcr

from .test_basics import BasicTestCase

from app.models import Sensor, Sample
from app.remote import usgs

my_vcr = vcr.VCR(
    # match_on=['method']
)


class TestUSGS(BasicTestCase):
    SITE_NUM = 235127
    U = usgs.USGS()

    @my_vcr.use_cassette('tests/fixtures/usgs_get_sample')
    def test_get_sample(self):
        sensor = Sensor.query.filter(Sensor.remote_type == 'usgs').first()
        before = Sample.query.count()
        self.U.get_sample(sensor.id)
        after = Sample.query.count()
        assert after > before

    @my_vcr.use_cassette('tests/fixtures/usgs_get_multiple_samples')
    def test_get_multiple_samples(self):
        sensors = Sensor.query.filter(Sensor.remote_type == 'usgs').all()
        sensor_ids = [sensor.id for sensor in sensors]
        before = Sample.query.count()
        self.U.get_multiple_samples(sensor_ids)
        after = Sample.query.count()
        assert after > before
