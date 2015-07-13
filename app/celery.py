"""
Starting our celery instance
"""
from __future__ import absolute_import

from celery import Celery

from config import Config

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
