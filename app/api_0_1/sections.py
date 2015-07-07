"""
Endpoints:
----------

- **/api/1.0/sections/** - **GET** List all sections
- **/api/1.0/sections/<id>** - **GET** Detailed information about section *id*
"""
from flask import jsonify, request, url_for, current_app

from ..models import Section
from .blueprint import api


@api.route('/sections/')
def get_sections():
    """
    List all sections

    Example response: ::

        { "count": 2,
          "next": null,
          "prev": null,
          "sections": [
            { "id": 2,
              "name": "Bear River",
              "url": "http://riverflo.ws/api/1.0/sections/2"
            },
            { "id": 1,
              "name": "Bull Branch",
              "url": "http://riverflo.ws/api/1.0/sections/1"
            }
          ]
        }
    """
    page = request.args.get('page', 1, type=int)
    pagination = Section.query.paginate(page,
                                        per_page=current_app.config['API_GAGES_PER_PAGE'],  # noqa
                                        error_out=False)
    sections = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_sections', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('.get_sections', page=page+1)
    return jsonify({
        'sections': [section.to_json() for section in sections],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/sections/<int:id>')
def get_section(id):
    """
    Detailed information about section *id*

    Parameters:
        id (int): Primary key for section

    Example response: ::

        { "access": null,
          "description": "Most commonly run from the where Goose Eye Brook",
          "id": 1,
          "latitude": 44.517188630525425,
          "location": "Ketchum, ME",
          "longitude": -70.93158602714539,
          "name": "Bull Branch",
          "regions": [
            { "html": "http://riverflo.ws/region/mahoosucs/",
              "id": 1,
              "name": "Mahoosuc Mountains",
              "url": "http://riverflo.ws/api/1.0/regions/1"
            },
            { "html": "http://127.0.0.1:5000/region/whites/",
              "id": 2,
              "name": "White Mountains",
              "url": "http://riverflo.ws/api/1.0/regions/2"
            },
            { "html": "http://riverflo.ws/region/maine/",
              "id": 4,
              "name": "Maine",
              "url": "http://riverflo.ws/api/1.0/regions/4"
            }
          ],
          "url": "http://riverflo.ws/api/1.0/sections/1"
        }
    """
    section = Section.query.get_or_404(id)
    return jsonify(section.to_long_json())
