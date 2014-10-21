#!/usr/bin/python

"""
App builder. Can be imported and used to start the site
"""

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	
	bootstrap.init_app(app)
	db.init_app(app)
	
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)
	
	from .api_1_0 import apiblueprint as api_1_0_blueprint
	app.register_blueprint(api_1_0_blueprint, url_prefix='/api/1.0/')
	
	return app