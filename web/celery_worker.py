#!/usr/bin/env python
import os

from app import create_app
from app.celery import celery
from app.tasks import remote

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()
