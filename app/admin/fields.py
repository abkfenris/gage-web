import json
from wtforms import Field
import geojson
from shapely.geometry import asShape
from geoalchemy2.shape import to_shape, from_shape
from wtforms.widgets import html_params, HTMLString
from geoalchemy2.elements import WKTElement, WKBElement
from flask import render_template
class WTFormsMapInput(object):
    def __call__(self, field, **kwargs):
        options = dict(name=field.name, value=field.data, height=field.height, width=field.width,
                       geometry_type=field.geometry_type)

        return HTMLString(render_template("admin/admin_map.html", height=options['height'], width=options['width'],
                                          geolayer=self.geolayer(field.data), preview=False))

    def geolayer(self, value):
        if value is not None:
            html = ""
            subme = """var geojson = JSON.parse('%s');
                       editableLayers.addData(geojson);
                       update()
                       map.fitBounds(editableLayers.getBounds());"""
            # If validation in Flask-Admin fails on somethign other than
            # the spatial column, it is never converted to geojson.  Didn't
            # spend the time to figure out why, so I just convert here.
            if isinstance(value, (WKTElement, WKBElement)):
                html += subme % geojson.dumps(to_shape(value))
            else:
                html += subme % geojson.dumps(value)
            return html


class WTFormsMapField(Field):
    widget = WTFormsMapInput()

    def __init__(self, label='', validators=None, geometry_type=None, width=500, height=500,
                 **kwargs):
        super(WTFormsMapField, self).__init__(label, validators, **kwargs)
        self.width = width
        self.height = height
        self.geometry_type = geometry_type

    def _value(self):
        """ Called by widget to get GeoJSON representation of object """
        if self.data:
            return self.data
        else:
            return json.loads(json.dumps(dict()))

    def process_formdata(self, valuelist):
        """ Convert GeoJSON to DB object """
        if valuelist:
            geo_ob = geojson.loads(valuelist[0])
            self.data = from_shape(asShape(geo_ob.geometry))
        else:
            self.data = None

    def process_data(self, value):
        """ Convert DB object to GeoJSON """
        if value is not None:
            self.data = geojson.loads(geojson.dumps(to_shape(value)))
            print self.data
        else:
            self.data = None