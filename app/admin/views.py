from flask import render_template

from . import admin

@admin.route('/')
def indexpage():
	return 'Hello Admin!'