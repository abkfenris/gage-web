"""
gages api imports api, app, db, auth, and models

Endpoints:
----------

- **/api/1.0/gages/** - **GET** List all gages
- **/api/1.0/gages/<id>** - **GET** Detailed information about gage number *id*
- **/api/1.0/gages/<id>/sample** - **POST** new sample data for gage *id*

"""

from flask import jsonify, request, url_for, current_app
from itsdangerous import JSONWebSignatureSerializer, BadSignature

from ..models import Gage
from . import api
from .errors import unauthorized


@api.route('/gages/')
def get_gages():
    """
    List all gages

    Example response: ::

        { "count": 5,
          "gages": [
            { "id": 2,
              "location": "Wild River near RT 2 in Gilead Maine",
              "name": "Wild River at Gilead",
              "url": "http://riverflo.ws/api/1.0/gages/2"
            },
            { "id": 3,
              "location": "Bear River near RT 2 in Newry Maine",
              "name": "Bear River at Newry",
              "url": "http://riverflo.ws/api/1.0/gages/3"
            }
          ],
          "next": "http://riverflo.ws/api/1.0/gages/?page=2",
          "prev": null
        }
    """
    page = request.args.get('page', 1, type=int)
    pagination = Gage.query.paginate(page,
                                     per_page=current_app.config['API_GAGES_PER_PAGE'],  # noqa
                                     error_out=False)
    gages = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_gages', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('.get_gages', page=page+1, _external=True)
    return jsonify({
        'gages': [gage.to_json() for gage in gages],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/gages/<int:id>')
def get_gage(id):
    """
    Detailed information about gage *id*

    Parameters:
        id (int): Primary id key of a gage

    Example response: ::

        { "html": "http://riverflo.ws/gage/androscoggin-rumford/",
          "id": 4,
          "location": null,
          "name": "Androscoggin River at Rumford",
          "regions": [
            { "html": "http://riverflo.ws/region/maine/",
              "id": 4,
              "name": "Maine",
              "url": "http://riverflo.ws/api/1.0/regions/4"
            }
          ],
          "sensors": [
            { "id": 10,
              "recent_sample": {
                "datetime": "Mon, 03 Nov 2014 18:15:00 GMT",
                "id": 5801,
                "url": "http://riverflo.ws/api/1.0/samples/5801",
                "value": 4.32
              },
              "type": "usgs-height",
              "url": "http://riverflo.ws/api/1.0/sensors/10"
            },
            { "id": 11,
              "recent_sample": {
                "datetime": "Mon, 03 Nov 2014 18:15:00 GMT",
                "id": 5866,
                "url": "http://riverflo.ws/api/1.0/samples/5866",
                "value": 3230.0
              },
              "type": "usgs-discharge",
              "url": "http://riverflo.ws/api/1.0/sensors/11"
            }
          ],
          "url": "http://riverflo.ws/api/1.0/gages/4"
        }
    """
    gage = Gage.query.get_or_404(id)
    return jsonify(gage.to_long_json())


@api.route('/gages/<int:id>/sample', methods=['POST'])
def gage_new_samples(id):
    """
    Submit new samples to gage *id*

    Parameters:
        id (int): Primary id key number of a gage

    Samples are formatted in body of request as a JSON Web Signature using the
    ``Gage.key``

    Example sample submitter: ::

        from itsdangerous import JSONWebSignatureSerializer
        import requests

        payload = {'samples':[
            {'type':'level',
             'value':16.7,
             'datetime': str(datetime.datetime.now())
             },
            {'type':'amps',
             'value':367.3,
             'datetime': str(datetime.datetime.now())
             },
            {'type':'voltage',
             'value':14.3,
             'datetime': str(datetime.datetime.now())
             },
            {'type':'discharge',
             'value':480,
             'datetime': str(datetime.datetime.now())
            }
            ],
            'gage':{
            'id':5
            }}

        s = JSONWebSignatureSerializer('<gage.key>')

        def submit(payload):
            data = s.dumps(payload)
            url = "http://riverflo.ws/api/1.0/gages/<gage.id>/sample"
            r = requests.post(url, data=data)
            if r.status_code is 200:
                return True
            else:
                return False

    If the key matches the stored key for the gage id in the url, \
    the server will iterate over the samples and add them to the database \
    creating new sensors for the gage if a new sample type is found. \
    Then the server will return JSON with a status code of 200.

    Example response: ::

        { 'gage': {u'id': 5,
            'location': 'Androscoggin River downstream of I-95 in Auburn ME',
            'name': 'Androscoggin River at Auburn',
            'url': 'http://riverflo.ws/api/1.0/gages/5'},
         'result': 'created',
         'samples': [{'datetime': 'Tue, 04 Nov 2014 20:43:39 GMT',
           'id': 10781,
           'url': 'http://riverflo.ws/api/1.0/samples/10781',
           'value': 16.7},
          {'datetime': 'Tue, 04 Nov 2014 20:43:39 GMT',
           'id': 10782,
           'url': 'http://riverflo.ws/api/1.0/samples/10782',
           'value': 367.3},
          {'datetime': 'Tue, 04 Nov 2014 20:43:39 GMT',
           'id': 10783,
           'url': 'http://riverflo.ws/api/1.0/samples/10783',
           'value': 14.3},
          {'datetime': 'Tue, 04 Nov 2014 20:43:39 GMT',
           'id': 10784,
           'url': 'http://riverflo.ws/api/1.0/samples/10784',
           'value': 480.0}]}

    If the signature does not match, the server will return JSON \
    with a status code of 401 - Unauthorized: ::

        {'error': 'unauthorized', 'message': 'bad signature'}

    """
    gage = Gage.query.get_or_404(id)
    s = JSONWebSignatureSerializer(gage.key)
    try:
        req_json = s.loads(request.data)
    except BadSignature:  # If the signature doesn't match
        return unauthorized('bad signature')
    except TypeError:  # Return unauthorized if no key defined for gage
        return unauthorized('bad signature')
    else:
        samples = req_json['samples']
        output = []
        print samples
        for sample in samples:
            result = gage.new_sample(stype=sample['type'].lower(),
                                     value=sample['value'],
                                     sdatetime=sample['datetime'])
            result_json = result.to_sensor_json()
            print result_json
            result_json['sender_id'] = sample['sender_id']
            print result_json
            output.append(result_json)
        return jsonify({
            'gage': gage.to_json(),
            'samples': output,
            'result': 'created'
        })
