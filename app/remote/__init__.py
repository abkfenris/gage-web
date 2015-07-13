import datetime

from app.database import db
from app.models import Sample


def add_new_sample(sensor_id, dt, svalue, deltaminutes=30):
    """
    Adds a new sample with an associacted remote sensor
    if there hasn't been a sample recorded within the last deltaminutes
    (default is 30).
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
