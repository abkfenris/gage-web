"""
Database builder
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

db = SQLAlchemy()

gage_sample_sql = text("""
SELECT g.name, g.slug, s.name, s.suffix, sa.datetime, sa.value
FROM gages g
, LATERAL (
    SELECT *
    FROM sensors
    WHERE gage_id = g.id
    ORDER BY sensors.id
    LIMIT 1
) s
, LATERAL (
    SELECT *
    FROM samples
    WHERE sensor_id = s.id
    AND datetime > NOW()::DATE-EXTRACT(DOW FROM NOW())::INTEGER-1
    ORDER BY samples.datetime DESC
    LIMIT 1
) sa
ORDER BY g.name""")


def gage_sample():
    """
    Returns a result proxy object which resolves to tuples of
        Gage Name
        Gage Slug
        Sensor Name
        Sensor Suffix
        Sample Datetime
        Sample Value
    """
    return db.engine.execute(gage_sample_sql)
