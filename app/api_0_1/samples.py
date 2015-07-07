"""
Endpoints:
----------

- **/api/1.0/samples/ - **GET** List all samples
- **/api/1.0/samples/<id> - **GET** Detailed information about sample *id*
"""
from flask import jsonify, request, url_for, current_app

from ..models import Sample
from .blueprint import api


@api.route('/samples/')
def get_samples():
    """
    List all samples

    Example response: ::

        { "count": 10696,
          "next": "http://riverflo.ws/api/1.0/samples/?page=2",
          "prev": null,
          "samples": [
            { "datetime": "Thu, 05 Jun 2014 13:50:27 GMT",
              "id": 52,
              "sensor": {
                "gage": {
                  "id": 2,
                  "location": "Wild River near RT 2 in Gilead Maine",
                  "name": "Wild River at Gilead",
                  "url": "http://riverflo.ws/api/1.0/gages/2"
                },
                "id": 5,
                "type": "level",
                "url": "http://riverflo.ws/api/1.0/sensors/5"
              },
              "url": "http://riverflo.ws/api/1.0/samples/52",
              "value": 24.0
            },
            { "datetime": "Thu, 05 Jun 2014 13:50:27 GMT",
              "id": 53,
              "sensor": {
                "gage": {
                  "id": 2,
                  "location": "Wild River near RT 2 in Gilead Maine",
                  "name": "Wild River at Gilead",
                  "url": "http://127.0.0.1:5000/api/1.0/gages/2"
                },
                "id": 8,
                "type": "volts",
                "url": "http://riverflo.ws/api/1.0/sensors/8"
              },
              "url": "http://riverflo.ws/api/1.0/samples/53",
              "value": 4.096
            }
          ]
        }
    """
    page = request.args.get('page', 1, type=int)
    pagination = Sample.query.paginate(page,
                                       per_page=current_app.config['API_GAGES_PER_PAGE'],  # noqa
                                       error_out=False)
    samples = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_samples', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('.get_samples', page=page+1, _external=True)
    return jsonify({
        'samples': [sample.to_json() for sample in samples],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/samples/<int:id>')
def get_sample(id):
    """
    Detailed information about sample *id*

    Parameters:
        id (int): Primary id key of sample

    Example response: ::

        { "datetime": "Thu, 05 Jun 2014 13:50:27 GMT",
          "id": 52,
          "sensor": {
            "gage": {
              "id": 2,
              "location": "Wild River near RT 2 in Gilead Maine",
              "name": "Wild River at Gilead",
              "url": "http://riverflo.ws/api/1.0/gages/2"
            },
            "id": 5,
            "type": "level",
            "url": "http://riverflo.ws/api/1.0/sensors/5"
          },
          "url": "http://riverflo.ws/api/1.0/samples/52",
          "value": 24.0
        }
    """
    sample = Sample.query.get_or_404(id)
    return jsonify(sample.to_json())
