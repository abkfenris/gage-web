"""

Endpoints:
----------

- **/api/1.0/regions/<id>** - **GET** Detailed information about region *id*
- **/api/1.0/rivers/ - **GET** List all rivers

"""
from flask import jsonify, request, url_for, current_app

from ..models import River
from .blueprint import api


@api.route('/rivers/')
def get_rivers():
    """
    List all rivers

    Example response: ::

        { "count": 7,
          "next": "http://riverflo.ws/api/1.0/sensors/?page=2",
          "prev": null,
          "rivers": [
            { "id": 1,
              "name": "Kennebec",
              "url": "http://riverflo.ws/api/1.0/rivers/1"
            },
            { "id": 2,
              "name": "Androscoggin",
              "url": "http://riverflo.ws/api/1.0/rivers/2"
            }
          ]
        }
    """
    page = request.args.get('page', 1, type=int)
    pagination = River.query.paginate(page,
                                      per_page=current_app.config['API_GAGES_PER_PAGE'],  # noqa
                                      error_out=False)
    rivers = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_rivers', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('.get_rivers', page=page+1, _external=True)
    return jsonify({
        'rivers': [river.to_json() for river in rivers],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/rivers/<int:id>')
def get_river(id):
    """
    Detailed information about river *id*

    Parameters:
        id (int): Primary id key for river

    Example response: ::

        { "downstream": {
            "id": 1,
            "name": "Kennebec",
            "url": "http://riverflo.ws/api/1.0/rivers/1"
          },
          "gages": [
            { "id": 5,
              "location": "Androscoggin River downstream of I-95 in Auburn ME",
              "name": "Androscoggin River at Auburn",
              "url": "http://riverflo.ws/api/1.0/gages/5"
            },
            { "id": 4,
              "location": "Androscoggin River below lower power plant",
              "name": "Androscoggin River at Rumford",
              "url": "http://riverflo.ws/api/1.0/gages/4"
            }
          ],
          "id": 2,
          "name": "Androscoggin",
          "sections": [],
          "tributaries": [
            { "id": 3,
              "name": "Sunday River",
              "url": "http://riverflo.ws/api/1.0/rivers/3"
            },
            { "id": 5,
              "name": "Wild River (Androscoggin)",
              "url": "http://riverflo.ws/api/1.0/rivers/5"
            },
            { "id": 6,
              "name": "Peapody River",
              "url": "http://riverflo.ws/api/1.0/rivers/6"
            },
            { "id": 7,
              "name": "Bear River (Androscoggin)",
              "url": "http://riverflo.ws/api/1.0/rivers/7"
            }
          ],
          "url": "http://riverflo.ws/api/1.0/rivers/2"
        }
    """
    river = River.query.get_or_404(id)
    return jsonify(river.to_long_json())
