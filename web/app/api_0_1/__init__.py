"""
Version 1.0 of the API for gages to connect and for others to be able to
retrieve data

Endpoints:
----------
- **/api/1.0/ - **GET** List basic routes
- **/api/1.0/gages/** - **GET** List all gages
- **/api/1.0/gages/<id>** - **GET** Detailed information about gage number *id*
- **/api/1.0/gages/<id>/sample** - **POST** new sample data for gage *id*
    - authenticated by individual gage secret key
- **/api/1.0/sensors/ - **GET** List all sensors
- **/api/1.0/sensors/<id> - **GET** Detailed information about sensor
- **/api/1.0/sensors/<id>/samples - **GET** Samples from sensor *id*
- **/api/1.0/samples/ - **GET** List all samples
- **/api/1.0/samples/<id> - **GET** Detailed information about sample *id*
- **/api/1.0/regions/** - **GET** List all regions
- **/api/1.0/regions/<id>** - **GET** Detailed information about region *id*
- **/api/1.0/rivers/ - **GET** List all rivers
- **/api/1.0/rivers/<id>** - **GET** Detained information about river *id*
- **/api/1.0/sections/** - **GET** List all sections
- **/api/1.0/sections/<id>** - **GET** Detailed information about section *id*
"""
from flask import jsonify, url_for

from .blueprint import api

# Import other API views
from . import gages, sensors, samples, rivers, sections, regions  # noqa


@api.route('/')
def indexpage():
    """**GET /api/1.0/**

    List of basic api routes
    """
    return jsonify({
        'gages': url_for('api.get_gages', _external=True),
        'sensors': url_for('api.get_sensors', _external=True),
        'samples': url_for('api.get_samples', _external=True),
        'rivers': url_for('api.get_rivers', _external=True),
        'sections': url_for('api.get_sections', _external=True),
        'regions': url_for('api.get_regions', _external=True),
    })
