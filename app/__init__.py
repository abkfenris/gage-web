#!/usr/bin/python

"""
App builder. Can be imported and used to start the site
"""

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask_debugtoolbar import DebugToolbarExtension


bootstrap = Bootstrap()
db = SQLAlchemy()
toolbar = DebugToolbarExtension()

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	
	bootstrap.init_app(app)
	db.init_app(app)
	toolbar.init_app(app)
	
	from main import main
	app.register_blueprint(main)
	
	#from admin import admin as admin_blueprint
	#app.register_blueprint(admin_blueprint, url_prefix='/admin')
	
	from admin import admin
	admin.init_app(app)
	
	from api_1_0 import api as api_1_0_blueprint
	app.register_blueprint(api_1_0_blueprint, url_prefix='/api/1.0')
	
	return app