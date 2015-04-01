"""
Main public interface to the website.
"""

from flask import Blueprint

main = Blueprint('main', __name__)

# importing views for blueprint
from . import views, errors, plot  # noqa
