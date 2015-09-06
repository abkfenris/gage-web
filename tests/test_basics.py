import unittest
from flask import current_app
from app import create_app, db
from app.models import Region, River, Section, Gage, Sensor, Sample, Correlation
import time
import datetime


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create some data to test against, but don't commit
        # Create a region
        maine = Region(name='Maine', slug='maine')
        db.session.add(maine)

        # Create a river
        andro = River(name='Androscoggin River',
                      slug='androscoggin')
        wild = River(name='Wild River of the Androsoggin',
                     slug='wild-river',
                     parent=andro)
        db.session.add(andro)
        db.session.add(wild)

        # Create a section
        wild_section = Section(name='Wild River from Hastings',
                               slug='hasting-to-gilead',
                               river=wild,
                               putin='SRID=4326;POINT(-71.05996191501617 44.31595096222731)',
                               takeout='SRID=4326;POINT(-70.97963511943817 44.390833083196924)',
                               path='SRID=4326;LINESTRING(-71.05997800827026 44.316024368364864,-71.05881929397583 44.31798950769032,-71.05731725692749 44.31884923545022,-71.05444192886353 44.31851148676115,-71.05298280715942 44.31943261497028,-71.05096578598022 44.322687152160796,-71.05045080184937 44.32449856163325,-71.04984998703003 44.32495908054771,-71.04761838912964 44.325849406864485,-71.04568719863892 44.32649411748597,-71.04306936264038 44.32753791965937,-71.04049444198608 44.327138821021585,-71.03847742080688 44.32664761897048,-71.03607416152954 44.32572660403795,-71.03517293930054 44.32554239931617,-71.03431463241577 44.32594150881567,-71.03341341018677 44.32805981378074,-71.03264093399048 44.329103588092785,-71.02929353713989 44.32984035877702,-71.02843523025513 44.33008594694842,-71.02757692337036 44.33137526797721,-71.02804899215698 44.33309431859246,-71.02783441543579 44.33459844654652,-71.02543115615845 44.33582627750024,-71.02311372756958 44.33714616710255,-71.0210108757019 44.33926406740166,-71.01598978042603 44.34328479806066,-71.01294279098511 44.3441441551062,-71.00916624069214 44.346752840399844,-71.0082221031189 44.34972966884455,-71.00689172744751 44.35107993293547,-71.00551843643188 44.351171995263435,-71.00393056869507 44.350374116950185,-71.00148439407349 44.35000586175751,-70.9984803199768 44.350374116950185,-70.99642038345337 44.35163230473401,-70.99328756332397 44.354117913402796,-70.9923005104065 44.3552225945275,-70.99212884902954 44.35678752380721,-70.99401712417603 44.357830786775374,-70.99517583847046 44.3607763701854,-70.99680662155151 44.36571602660432,-70.99599123001099 44.368722570068854,-70.99448919296265 44.36961223191264,-70.99242925643921 44.37123813071097,-70.99054098129272 44.371422191881805,-70.98955392837524 44.372986688478704,-70.99075555801392 44.37507261892906,-70.98963975906372 44.37691308409485,-70.98848104476929 44.37832406821415,-70.9874939918518 44.38086988832067,-70.98470449447632 44.382403461463625,-70.98273038864136 44.384059675338044,-70.9810996055603 44.38531713976433,-70.97848176956177 44.3864825704798,-70.97749471664429 44.38746396782254,-70.97903966903687 44.38970271892836)',)
        db.session.add(wild_section)

        # Create a gage
        wild_gage = Gage(name='Wild River at Gilead',
                         slug='wild-river-gilead',
                         point='SRID=4326;POINT(-70.97963511943817 44.390833083196924)',
                         river=wild,
                         visible=True,
                         zipcode='04217',
                         local_town='Gilead, ME',
                         location='Wild River at Gilead above Rt 2',
                         key='password')
        db.session.add(wild_gage)

        # Create a sensor
        wild_sensor = Sensor(name='Gage Height',
                             stype='usgs-height',
                             local=False, remote_type='usgs',
                             remote_id='01054200',
                             gage=wild_gage)
        diamond_height = Sensor(name='Gage Height',
                                stype='usgs-height',
                                local=False, remote_type='usgs',
                                remote_id='01052500')
        diamond_discharge = Sensor(name='Discharge',
                                   stype='usgs-discharge',
                                   local=False, remote_type='usgs',
                                   remote_id='01052500',
                                   remote_parameter='00060')
        rapid_cfs = Sensor(name='Rapid CFS',
                           stype='h2oline-cfs',
                           local=False, remote_type='h2oline',
                           remote_id='235127')
        azicohos_level = Sensor(name='Aziscohol height',
                                stype='h2oline-height',
                                local=False, remote_type='h2oline',
                                remote_id='235130',
                                remote_parameter='FT')
        neilson_flow = Sensor(name='Neilson flow',
                              stype='cehq-flow',
                              local=False, remote_type='cehq',
                              remote_id='050915')
        skeena_level = Sensor(name='Skeena Level',
                              stype='cawater-level',
                              local=False, remote_type='cawater',
                              remote_id='BC_08EB003')
        humber_level = Sensor(name='Humber Level',
                              stype='cawater-level',
                              local=False, remote_type='cawater',
                              remote_id='NL_02YL012')
        cheakamus_discharge = Sensor(name='Cheakamus Discharge',
                                     stype='cawater-discharge',
                                     local=False, remote_type='cawater',
                                     remote_id='BC_08GA043',
                                     remote_parameter='discharge')
        canaseraga_stage = Sensor(name='Canaseraga Creek',
                                  stype='canaseraga-stage',
                                  local=False, remote_type='corps',
                                  remote_id='DSVN6')
        db.session.add(wild_sensor)
        db.session.add(diamond_height)
        db.session.add(diamond_discharge)
        db.session.add(rapid_cfs)
        db.session.add(azicohos_level)
        db.session.add(neilson_flow)
        db.session.add(skeena_level)
        db.session.add(humber_level)
        db.session.add(canaseraga_stage)

        # Create a sample
        wild_sample = Sample(sensor=wild_sensor,
                             datetime=datetime.datetime.now(),
                             value=5.8)
        db.session.add(wild_sample)
        wild_correlation = Correlation(sensor=wild_sensor,
                                       section=wild_section,
                                       minimum=3.5,
                                       low=4.0,
                                       medium=5.0,
                                       high=6.0,
                                       huge=9.0)
        db.session.add(wild_correlation)
        db.session.commit()

        # Create a correlation
        # wild_correlation = Correlation(section=wild_section,)

    def tearDown(self):
        # time.sleep(60)
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class AppTest(BasicTestCase):

    def test_app_exists(self):
        """
        App exists (test_basics.AppTest)
        """
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """
        App is in testing config (test_basics.AppTest)
        """
        self.assertTrue(current_app.config['TESTING'])
