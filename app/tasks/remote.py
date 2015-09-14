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
CORPS = corps.Corps()
Failure = base.RemoteGage()


sources = {
    'h2oline': H2Oline.get_multiple_samples,
    'usgs': USGS.get_multiple_samples,
    'cehq': CEHQ.get_multiple_samples,
    'cawater': CAWaterOffice.get_multiple_samples,
    'corps': CORPS.get_multiple_samples
}


class UnknownSource(Exception):
    """
    Raised when an unknown remote_type is used
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def missing_multiple_samples(sensor_ids):
    """
    If a remote_type is missing from sources then raise an error
    with the sensor ids with the remote type
    """
    raise UnknownSource('Unknown remote_type for %s', ', '.join(sensor_ids))


@celery.task
def fetch_samples(sensor_ids, remote_type, remote_parameter):
    """
    Fetch samples for a group of sensor_ids with the same remote_type
    and remote_parameter
    """
    logger.info('Fetching a chunk of %s samples for sensors %s', remote_type, sensor_ids)
    sources.get(remote_type, missing_multiple_samples)(sensor_ids)


def chunk_sensor_ids(sensor_ids, remote_type, remote_parameter, delay):
    """
    Break down tasks into smaller bits based on SAMPLES_PER_CHUNK size
    then execute fetch_samples (normally as a celery task)
    """
    logger.info('Chunking %s sensors for tasks for sensors %s', remote_type, sensor_ids)
    try:
        x_range = xrange
    except NameError:
        x_range = range
    for chunk in [sensor_ids[x:x+SAMPLES_PER_CHUNK] for x in
                  x_range(0, len(sensor_ids), SAMPLES_PER_CHUNK)]:
        if delay:
            fetch_samples.delay(chunk, remote_type, remote_parameter)
        else:
            fetch_samples(chunk, remote_type, remote_parameter)


@periodic_task(run_every=(crontab(minute='*/15')),
               name='fetch_remote_samples',
               ignore_result=True)
def fetch_remote_samples(delay=True):
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
        chunk_sensor_ids(group[0], group[1], group[2], delay)
