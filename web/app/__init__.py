#!/usr/bin/python

"""
App builder. Can be imported and used to start the site
"""
import os

from flask import Flask
from flask_bootstrap import Bootstrap
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
sentry = Sentry()

from .models import user_datastore

logging_map = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}




def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    bootstrap.init_app(app)

    db.init_app(app)
    security.init_app(app, user_datastore)
    toolbar.init_app(app)

    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging_map[log_level])
    stream = logging.StreamHandler()
    stream.setLevel(logging_map[log_level])
    logger.addHandler(stream)

    if config_name in ('docker', 'development', 'production'):
        sentry.init_app(app, logging=True, level=logging.INFO)
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
