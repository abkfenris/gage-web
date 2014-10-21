from app import app, db

from auth import *
from admin import admin
from api import api
from models import *
from views import *

admin.setup()
#api.setup()

if __name__ == '__main__':
	User.create_table(fail_silently=True)
	Region.create_table(fail_silently=True)
	Gage.create_table(fail_silently=True)
	Sample.create_table(fail_silently=True)
	app.run(host='0.0.0.0')