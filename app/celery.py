"""
Starting our celery instance
"""
from __future__ import absolute_import

import logging
import os

from celery import Celery
from flask import current_app
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal
from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging

from config import Config, config

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

env = os.environ.get('FLASK_CONFIG', 'default')
if env in ('production', 'development', 'default'):
    client = Client(config[env].SENTRY_DSN)
    handler = SentryHandler(client)
    setup_logging(handler)
    register_logger_signal(client, loglevel=logging.INFO)
    register_signal(client)

TaskBase = celery.Task


class ContextTask(TaskBase):
    abstract = True

    def __call__(self, *args, **kwargs):
        with current_app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)

celery.Task = ContextTask
