#!/usr/bin/python

"""
App builder. Can be imported and used to start the site
"""

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask_security import Security
from flask_debugtoolbar import DebugToolbarExtension
import logging
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix

from config import config
from .database import db

bootstrap = Bootstrap()
security = Security()
toolbar = DebugToolbarExtension()

from .models import user_datastore


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    bootstrap.init_app(app)

    db.init_app(app)
    security.init_app(app, user_datastore)
    toolbar.init_app(app)

    if config_name in ('production', 'development', 'default'):
        sentry = Sentry(app, logging=True, level=logging.INFO)
        app.wsgi_app = ProxyFix(app.wsgi_app)

    from app.celery import celery
    celery.conf.update(app.config)

    from .main import main
    app.register_blueprint(main)

    from .admin import admin
    admin.init_app(app)

    from .api_0_1 import api as api_0_1_blueprint
    app.register_blueprint(api_0_1_blueprint, url_prefix='/api/0.1')

    return app
