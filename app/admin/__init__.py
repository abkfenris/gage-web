from flask.ext.admin import Admin
from flask.ext.admin.contrib.geoa import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
import os.path as op

from .. import db
from ..models import User, Region, River, Section, Gage, Sensor

path = op.join(op.dirname(__file__), '../static/images')


class SectionView(ModelView):
    column_list = ('name', 'path', 'slug', 'river', 'location')
    column_labels = dict(slug='URL Slug')
    column_searchable_list = ('name', River.name)
    form_widget_args = {'putin': {'data-height': 400, 'data-width': 400},
                        'takeout': {'data-height': 200, 'data-width': 200},
                        'path': {'data-height': 600, 'data-width': 600}}


class GageView(ModelView):
    can_create = True
    column_exclude_list = ('key',
                           'elevationUnits',
                           'zipcode',
                           'visible',
                           'elevation',
                           'backend_notes',
                           'description',
                           'short_description',
                           'started',
                           'ended')
    column_labels = dict(slug='URL Slug')
    column_searchable_list = ('name',
                              River.name,
                              'slug',
                              'local_town',
                              'location')
    # inline_models = (Sensor,)
    form_widget_args = {'point': {'data-height': 500, 'data-width': 500}}


admin = Admin(name="Riverflo.ws")
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Region, db.session))
admin.add_view(ModelView(River, db.session))
admin.add_view(SectionView(Section, db.session))
admin.add_view(GageView(Gage, db.session))
admin.add_view(ModelView(Sensor, db.session))
admin.add_view(FileAdmin(path, '/static/images/', name='Images'))
