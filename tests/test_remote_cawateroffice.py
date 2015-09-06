import datetime

import vcr

from .test_basics import BasicTestCase

from app.remote import cawateroffice
from app.models import Sensor, Sample

my_vcr = vcr.VCR(
    # match_on=['method']
)


class TestWaterOffice(BasicTestCase):
    SITES = ['BC_07EA004', 'NL_02YL012', 'AB_05CA004', 'MB_05PF062',
             'NB_01AL002', 'NT_10FB001', 'NS_01FC002', 'NU_06JC002',
             'ON_02KB001', 'PE_01CB002', 'QC_02OB011', 'SK_05JK007',
             'YT_08AB001']
    WO = cawateroffice.WaterOffice()

    @my_vcr.use_cassette('tests/fixtures/cawateroffice_get_from_wateroffice')
    def test_get_from_wateroffice(self):
        for site_num in self.SITES:
            dt, level, discharge = self.WO.get_from_wateroffice(site_num)
            assert type(level) == float
            assert type(dt) == datetime.datetime
            try:
                assert type(discharge) == float
            except AssertionError:
                assert discharge is None

    @my_vcr.use_cassette('tests/fixtures/cawateroffice_get_sample')
    def test_get_sample(self):
        sensor = Sensor.query.filter(Sensor.remote_type == 'cawater').first()
        before = Sample.query.count()
        self.WO.get_sample(sensor.id)
        after = Sample.query.count()
        assert after > before

    @my_vcr.use_cassette('tests/fixtures/cawateroffice_get_multiple_samples')
    def test_get_multiple_samples(self):
        sensors = Sensor.query.filter(Sensor.remote_type == 'cawater').all()
        sensor_ids = [sensor.id for sensor in sensors]
        before = Sample.query.count()
        self.WO.get_multiple_samples(sensor_ids)
        after = Sample.query.count()
        assert after > before
