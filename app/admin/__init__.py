#from flask import Blueprint
#
#admin = Blueprint('admin', __name__)
#
#from . import views

from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.admin.model.form import InlineFormAdmin
import os.path as op
from .. import db
from ..models import User, Region, River, Section, Gage, Sensor

path = op.join(op.dirname(__file__), '../static/images')

class SectionView(ModelView):
	column_list = ('name', 'slug', 'river', 'location')
	column_labels = dict(slug='URL Slug')
	column_searchable_list = ('name', River.name)

class GageView(ModelView):
	column_exclude_list = ('point', 'key', 'elevationUnits', 'zipcode', 'visible', 'elevation', 'backend_notes', 'description', 'short_description', 'started', 'ended')
	column_labels = dict(slug='URL Slug')
	column_searchable_list = ('name', River.name, 'slug', 'local_town', 'location')
	inline_models = (Sensor,)


admin = Admin(name="Riverflo.ws")
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Region, db.session))
admin.add_view(ModelView(River, db.session))
admin.add_view(SectionView(Section, db.session))
admin.add_view(GageView(Gage, db.session))
admin.add_view(FileAdmin(path, '/static/images/', name='Images'))