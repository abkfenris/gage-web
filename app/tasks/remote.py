"""
Celery tasks for fetching remote samples
"""
import logging

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from sqlalchemy import func

from app.database import db
from app.models import Sensor
from app.remote import h2oline, usgs, cehq, cawateroffice, corps, base
from app.celery import celery

logger = logging.getLogger(__name__)

SAMPLES_PER_CHUNK = 25

H2Oline = h2oline.H2Oline()
USGS = usgs.USGS()
CEHQ = cehq.CEHQ()
CAWaterOffice = cawateroffice.WaterOffice()
Corps = corps.Corps()
Failure = base.RemoteGage()


sources = {
    'h2oline': H2Oline.get_multiple_samples,
    'usgs': USGS.get_multiple_samples,
    'cehq': CEHQ.get_multiple_samples,
    'cawater': CAWaterOffice.get_multiple_samples,
    'corps': Corps.get_multiple_samples
}


@celery.task
def fetch_usgs_level_samples_chunk(sensor_id_list):
    """
    Fetch an individual chunk of samples from the usgs sensors
    """
    logger.info('Fetching multiple USGS level samples for sensors %s',
                sensor_id_list)
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
    logger.info('Fetching USGS samples for %s', sensor_id)
    usgs.get_other_sample(sensor_id)


@celery.task
def fetch_h2oline_sample(sensor_id):
    """
    Fetch h2oline sample
    """
    logger.info('Fetching H2Oline samples for %s', sensor_id)
    h2oline.get_sample(sensor_id)


@celery.task
def fetch_cehq_sample(sensor_id):
    """
    Fetch cehq sample
    """
    logger.info('Fetching CEHQ samples for %s', sensor_id)
    cehq.get_sample(sensor_id)


def missing_multiple_samples(sensor_ids):
    logger.error('Unknown remote_type for %s', ', '.join(sensor_ids))


@celery.task
def fetch_samples(sensor_ids, remote_type, remote_parameter):
    sources.get(remote_type, missing_multiple_samples)(sensor_ids)


def chunk_sensor_ids(sensor_ids, remote_type, remote_parameter):
    """
    Break down tasks into smaller bits based on SAMPLES_PER_CHUNK size
    """
    try:
        x_range = xrange
    except NameError:
        x_range = range
    for chunk in [sensor_ids[x:x+SAMPLES_PER_CHUNK] for x in
                  x_range(0, len(sensor_ids), SAMPLES_PER_CHUNK)]:
        fetch_samples.delay(chunk, remote_type, remote_parameter)


@periodic_task(run_every=(crontab(minute='*/15')),
               name='fetch_remote_samples',
               ignore_result=True)
def fetch_remote_samples():
    """
    Create tasks for all remote sensors to be updated
    """
    # Fetch remote USGS level gages
    logger.info('Fetching remote samples')
    remote_sensors = db.session.query(func.array_Agg(Sensor.id),
                                      Sensor.remote_type,
                                      Sensor.remote_parameter)\
                               .group_by(Sensor.remote_type,
                                         Sensor.remote_parameter)\
                               .filter(Sensor.local == False).all()
    for group in remote_sensors:
        chunk_sensor_ids(group[0], group[1], group[2])
