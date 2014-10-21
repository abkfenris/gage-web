#!/usr/bin/python

"""
App builder. Can be imported and used to start the site
"""

from flask import Flask

from flask_peewee.db import Database

from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig') #http://stackoverflow.com/questions/15122312/how-to-import-from-config-file-in-flask & Flask Web Development p.200
#app.config.from_envar('GAGE_WEB_SETTINGS') #http://flask.pocoo.org/docs/config/

db = SQLAlchemy(app)