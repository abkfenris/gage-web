"""
Main public interface to the website.
"""

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors, plot
