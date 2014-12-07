#from flask import Blueprint
#
#admin = Blueprint('admin', __name__)
#
#from . import views

from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.geoa import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.admin.model.form import InlineFormAdmin
import os.path as op
from .. import db
from ..models import User, Region, River, Section, Gage, Sensor
#from .fields import WTFormsMapField

path = op.join(op.dirname(__file__), '../static/images')

class SectionView(ModelView):
	column_list = ('name', 'path', 'slug', 'river', 'location')
	column_labels = dict(slug='URL Slug')
	column_searchable_list = ('name', River.name)
	form_widget_args = {'putin':{'data-height':400, 'data-width':400},
	                    'takeout': {'data-height': 200, 'data-width': 200},
	                    'path': {'data-height':600, 'data-width': 600}}
	#form_overrides = dict(putin=WTFormsMapField)
	#form_args = dict(
	#	putin = dict(
	#		geometry_type='Point', height=500, width=500
	#	)
	#)
	
	#def scaffold_form(self):
	#	form_class = super(SectionView, self).scaffold_form()
	#	form_class.putin = WTFormsMapField()
	#	return form_class
	

class GageView(ModelView):
	can_create = True
	column_exclude_list = ('key', 'elevationUnits', 'zipcode', 'visible', 'elevation', 'backend_notes', 'description', 'short_description', 'started', 'ended')
	column_labels = dict(slug='URL Slug')
	column_searchable_list = ('name', River.name, 'slug', 'local_town', 'location')
	#inline_models = (Sensor,)
	#form_overrides = dict(point=WTFormsMapField)
	form_widget_args = {'point':{'data-height': 500, 'data-width': 500}}
	
	#def __init__(self, Gage, session, **kwargs):
	#	super(GageView, self).__init__(Gage, session, **kwargs)
	#
	#def scaffold_form(self):
	#	form_class = super(GageView, self).scaffold_form()
	#	form_class.point = WTFormsMapField()
	#	return form_class
	

admin = Admin(name="Riverflo.ws")
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Region, db.session))
admin.add_view(ModelView(River, db.session))
admin.add_view(SectionView(Section, db.session))
admin.add_view(GageView(Gage, db.session))
admin.add_view(FileAdmin(path, '/static/images/', name='Images'))