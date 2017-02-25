import datetime
import logging

from app.database import db
from app.models import Sample, Sensor

logger = logging.getLogger(__name__)


def add_new_sample(sensor_id, dt, svalue, deltaminutes=10):
    """
    Adds a new sample with an associacted remote sensor
    if there hasn't been a sample recorded within the last deltaminutes
    (default is 10).
    Arguments:
        sensor_id (int): Primary key for sensor
        dt (datetime): Datetime of sample
        svalue (float): Value of sample
    """
    delta = datetime.datetime.now() - datetime.timedelta(minutes=deltaminutes)
    sample = Sample.query.filter_by(sensor_id=sensor_id)\
                         .order_by(Sample.datetime.desc()).first()
    if sample is None or (sample.datetime < delta and
                          (sample.datetime != dt.replace(tzinfo=None))):
        new_sample = Sample(sensor_id=sensor_id,
                            value=svalue,
                            datetime=dt)
        db.session.add(new_sample)
        db.session.commit()
        logger.debug('Saved sample (%s - %s - %s) for sensor %s',
                     new_sample.id,
                     svalue,
                     dt,
                     sensor_id)
    else:
        message = ''
        if sample.datetime == dt.replace(tzinfo=None):
            message = message + 'Sample times are the same. '
        if sample.datetime < delta:
            message = message + 'Last sample was more than {0} min ago '.format(deltaminutes)
        else:
            message = message + 'Last sample was less than {0} min ago '.format(deltaminutes)
        logger.warning('Discarded sample (%s - %s) for sensor %s, compared to (%s - %s). %s',
                       svalue,
                       dt,
                       sensor_id,
                       sample.value,
                       sample.datetime,
                       message)


class RemoteGage(object):
    """
    Base abstraction of the gage updating process
    """
    def sensor(self, sensor_id):
        """
        Returns selected sensor object
        """
        return Sensor.query.get(sensor_id)

    def get_sample(self, sensor_id):
        """
        Get a single sample and save latest values
        """
        raise NotImplementedError

    def get_multiple_samples(self, sensor_ids):
        """
        Smartly get multiple samples if possible and save latest values
        """
        for sensor_id in sensor_ids:
            self.get_sample(sensor_id)
