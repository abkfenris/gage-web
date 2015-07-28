"""
Celery tasks for fetching remote samples
"""
import logging

from celery.task.schedules import crontab
from celery.decorators import periodic_task

from app.models import Sensor
from app.remote import h2oline, usgs
from app.celery import celery

logger = logging.getLogger(__name__)


@celery.task
def fetch_usgs_level_samples_chunk(sensor_id_list):
    """
    Fetch an individual chunk of samples from the usgs sensors
    """
    logger.info('Fetching multiple USGS level samples for sensors {0}'
                .format(sensor_id_list))
    usgs.get_multiple_level(sensor_id_list)


@celery.task
def fetch_usgs_level_samples_all(sensor_id_list):
    """
    Fetch USGS level samples from the USGS Instantaneous Values Web Service
    http://waterservices.usgs.gov/rest/IV-Service.html#Multiple
    This service can return up to 100 gages worth at a time.
    """
    samples_per_request = 2
    # dealing with python 3 renaming xrange
    try:
        x_range = xrange
    except NameError:
        x_range = range
    for chunk in [sensor_id_list[x:x+samples_per_request] for x in
                  x_range(0, len(sensor_id_list), samples_per_request)]:
        fetch_usgs_level_samples_chunk(chunk)


@celery.task
def fetch_usgs_other_sample(sensor_id):
    """
    Fetch other types of USGS samples, 1 sensor at a time
    """
    logger.info('Fetching USGS samples for {0}'.format(sensor_id))
    usgs.get_other_sample(sensor_id)


@celery.task
def fetch_h2oline_sample(sensor_id):
    """
    Fetch h2oline sample
    """
    logger.info('Fetching H2Oline samples for {0}'.format(sensor_id))
    h2oline.get_sample(sensor_id)


@periodic_task(run_every=(crontab(minute='*/15')),
               name='fetch_remote_samples',
               ignore_result=True)
def fetch_remote_samples():
    """
    Create tasks for all remote sensors to be updated
    """
    # Fetch remote USGS level gages
    logger.info('Fetching remote samples')
    usgs_level_sensors = Sensor.query.filter_by(local=False,
                                                remote_type='usgs',
                                                remote_parameter=None)\
                                     .with_entities(Sensor.id).all()
    fetch_usgs_level_samples_all.delay([sensor[0] for sensor in usgs_level_sensors])

    # Fetch other USGS gages
    usgs_other_sensors = Sensor.query.filter(Sensor.local == False,
                                             Sensor.remote_type == 'usgs',
                                             Sensor.remote_parameter != None)\
                                     .with_entities(Sensor.id).all()
    for sensor in usgs_other_sensors:
        fetch_usgs_other_sample.delay(sensor[0])

    # Fetch h2oline gages
    other_remote_sensors = Sensor.query.filter(Sensor.local == False,
                                               Sensor.remote_type == 'h2oline')\
                                       .with_entities(Sensor.id).all()
    for sensor in other_remote_sensors:
        fetch_h2oline_sample.delay(sensor[0])
