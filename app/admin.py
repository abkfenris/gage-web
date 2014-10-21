"""
Admin interface, sets up the admin views and sorting
"""

from flask_peewee.admin import Admin, ModelAdmin

from app import app, db
from auth import auth
from models import User, Gage, Region, Sample

class RegionAdmin(ModelAdmin):
	columns = ('name', 'shortDescription')

class GageAdmin(ModelAdmin):
	columns = ('name', 'location')
	#foreign_key_lookups = {'region': 'name'}

class SampleAdmin(ModelAdmin):
	columns = ('gage', 'timestamp', 'level', 'battery')



admin = Admin(app, auth)

admin.register(Gage, GageAdmin)
admin.register(Region, RegionAdmin)
admin.register(Sample, SampleAdmin)

auth.register_admin(admin)