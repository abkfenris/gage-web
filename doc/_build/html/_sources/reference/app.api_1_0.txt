app.api_1_0 package
===================

Version 1.0 of the API for gages to connect and for others to be able to retrieve data

Endpoints:
----------
- **/api/1.0/ - **GET** List basic routes
- **/api/1.0/gages/** - **GET** List all gages
- **/api/1.0/gages/<id>/** - **GET** Detailed information about gage number *id*
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





Module contents
---------------

.. automodule:: app.api_1_0
    :members:
    :undoc-members:
    :show-inheritance:

Submodules
----------

app.api_1_0.errors module
-------------------------

.. automodule:: app.api_1_0.errors
    :members:
    :undoc-members:
    :show-inheritance:

app.api_1_0.gages module
------------------------

.. automodule:: app.api_1_0.gages
    :members:
    :undoc-members:
    :show-inheritance:

app.api_1_0.regions module
--------------------------

.. automodule:: app.api_1_0.regions
    :members:
    :undoc-members:
    :show-inheritance:

app.api_1_0.rivers module
-------------------------

.. automodule:: app.api_1_0.rivers
    :members:
    :undoc-members:
    :show-inheritance:

app.api_1_0.samples module
--------------------------

.. automodule:: app.api_1_0.samples
    :members:
    :undoc-members:
    :show-inheritance:

app.api_1_0.sections module
---------------------------

.. automodule:: app.api_1_0.sections
    :members:
    :undoc-members:
    :show-inheritance:

app.api_1_0.sensors module
--------------------------

.. automodule:: app.api_1_0.sensors
    :members:
    :undoc-members:
    :show-inheritance:



