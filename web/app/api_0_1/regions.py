"""
Endpoints:
----------

- **/api/1.0/regions/** - **GET** List all regions
- **/api/1.0/regions/<id>** - **GET** Detailed information about region *id*
"""

from flask import jsonify, request, url_for, current_app

from ..models import Region
from .blueprint import api


@api.route('/regions/')
def get_regions():
    """
    List all regions

    Example response: ::

        { "count": 5,
          "next": "http://riverflo.ws/api/1.0/regions/?page=2",
          "prev": null,
          "regions": [
            { "html": "http://riverflo.ws/region/mahoosucs/",
              "id": 1,
              "name": "Mahoosuc Mountains",
              "url": "http://riverflo.ws/api/1.0/regions/1"
            },
            { "html": "http://riverflo.ws/region/whites/",
              "id": 2,
              "name": "White Mountains",
              "url": "http://riverflo.ws/api/1.0/regions/2"
            }
          ]
        }

    """
    page = request.args.get('page', 1, type=int)
    pagination = Region.query.paginate(page,
                                       per_page=current_app.config['API_GAGES_PER_PAGE'],  # noqa
                                       error_out=False)
    regions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_regions', page=page-1, _external=True)
    next_p = None
    if pagination.has_next:
        next_p = url_for('.get_regions', page=page+1, _external=True)
    return jsonify({
        'regions': [region.to_json() for region in regions],
        'prev': prev,
        'next': next_p,
        'count': pagination.total
    })


@api.route('/regions/<int:rid>')
def get_region(rid):
    """
    Detailed information about region *id*

    Parameters:
        id (int): Primary id key of region

    Example response: ::

        { "description": "The Mahoosuc Mountains are in Maine.",
          "gages": [
            { "id": 3,
              "location": "Bear River near RT 2 in Newry Maine",
              "name": "Bear River at Newry",
              "url": "http://riverflo.ws/api/1.0/gages/3"
            },
            { "id": 1,
              "location": "Bull Branch at Twin Bridges in Ketchum Maine",
              "name": "Bull Branch",
              "url": "http://riverflo.ws/api/1.0/gages/1"
            }
          ],
          "html": "http://riverflo.ws/region/mahoosucs/",
          "id": 1,
          "name": "Mahoosuc Mountains",
          "sections": [
            { "id": 2,
              "name": "Bear River",
              "url": "http://riverflo.ws/api/1.0/sections/2"
            },
            { "id": 1,
              "name": "Bull Branch",
              "url": "http://riverflo.ws/api/1.0/sections/1"
            }
          ],
          "url": "http://riverflo.ws/api/1.0/regions/1"
        }
    """
    region = Region.query.get_or_404(rid)
    return jsonify(region.to_long_json())
