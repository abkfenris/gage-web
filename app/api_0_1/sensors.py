"""
Endpoints:
----------

- **/api/1.0/sensors/ - **GET** List all sensors
- **/api/1.0/sensors/<id> - **GET** Detailed information about sensor
- **/api/1.0/sensors/<id>/samples - **GET** Samples from sensor *id*
"""
from flask import jsonify, request, url_for, current_app

from ..models import Sensor, Sample
from .blueprint import api


@api.route('/sensors/')
def get_sensors():
    """
    List all sensors

    Example response: ::

        { "count": 17,
          "next": "http://riverflo.ws/api/1.0/sensors/?page=2",
          "prev": null,
          "sensors": [
            { "id": 2,
              "type": "voltage",
              "url": "http://riverflo.ws/api/1.0/sensors/2"
            },
            { "id": 3,
              "type": "amps",
              "url": "http://riverflo.ws/api/1.0/sensors/3"
            }
          ]
        }
    """
    page = request.args.get('page', 1, type=int)
    pagination = Sensor.query.paginate(page,
                                       per_page=current_app.config['API_GAGES_PER_PAGE'],  # noqa
                                       error_out=False)
    sensors = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_sensors', page=page-1, _external=True)
    next_p = None
    if pagination.has_next:
        next_p = url_for('.get_sensors', page=page+1, _external=True)
    return jsonify({
        'sensors': [sensor.to_json() for sensor in sensors],
        'prev': prev,
        'next': next_p,
        'count': pagination.total
    })


@api.route('/sensors/<int:sid>')
def get_sensor(sid):
    """
    Detailed information about sensor *id*

    Parameters:
        id (int): Primary id key of sensor

    Example response: ::

        { "description": null,
          "ended": null,
          "gage": {
            "id": 2,
            "location": "Wild River near RT 2 in Gilead Maine",
            "name": "Wild River at Gilead",
            "url": "http://riverflo.ws/api/1.0/gages/2"
          },
          "id": 5,
          "maximum": null,
          "minimum": null,
          "recent_sample": {
            "datetime": "Mon, 25 Aug 2014 13:11:35 GMT",
            "id": 1555,
            "url": "http://riverflo.ws/api/1.0/samples/1555",
            "value": 25.6666666666667
          },
          "started": null,
          "type": "level",
          "url": "http://riverflo.ws/api/1.0/sensors/5"
        }
    """
    sensor = Sensor.query.get_or_404(sid)
    return jsonify(sensor.to_long_json())


@api.route('/sensors/<int:sid>/samples')
def get_sensor_samples(sid):
    """
    List samples for sensor *id*

    Parameters:
        id (int): Primary id key of sensor

    Example response: ::

        { "count": 487,
          "next": null,
          "prev": null,
          "samples": [
            { "datetime": "Thu, 05 Jun 2014 13:50:27 GMT",
              "id": 52,
              "url": "http://riverflo.ws/api/1.0/samples/52",
              "value": 24.0
            },
            { "datetime": "Thu, 05 Jun 2014 13:50:42 GMT",
              "id": 55,
              "url": "http://riverflo.ws/api/1.0/samples/55",
              "value": 24.0
            }
          ],
          "sensor": {
            "id": 5,
            "type": "level",
            "url": "http://riverflo.ws/api/1.0/sensors/5"
          }
        }
    """
    sensor = Sensor.query.get_or_404(sid)
    page = request.args.get('page', 1, type=int)
    pagination = Sample.query.filter_by(sensor_id=sid).paginate(page,
                                                                per_page=current_app.config['API_GAGES_PER_PAGE'],  # noqa
                                                                error_out=False)
    samples = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_sensor_samples', page=page-1)
    next_p = None
    if pagination.has_next:
        next_p = url_for('.get_sensor_samples', page=page+1)
    return jsonify({
        'sensor': sensor.to_json(),
        'samples': [sample.to_sensor_json() for sample in samples],
        'prev': prev,
        'next': next_p,
        'count': pagination.total,
    })
