"""
Endpoints:
----------

- **/api/1.0/sections/** - **GET** List all sections
- **/api/1.0/sections/<id>** - **GET** Detailed information about section *id*
"""
from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Section
from . import api

@api.route('/sections/')
def get_sections():
	page = request.args.get('page', 1, type=int)
	pagination = Section.query.paginate(page, per_page=current_app.config['API_GAGES_PER_PAGE'], error_out=False)
	sections = pagination.items
	prev = None
	if pagination.has_prev:
		prev = url_for('.get_sections', page=page-1)
	next = None
	if pagination.has_next:
		next = url_for('.get_sections', page=page+1)
	return jsonify({
		'sensors': [section.to_json() for section in sections],
		'prev': prev,
		'next': next,
		'count': pagination.total
	})

@api.route('/sections/<int:id>')
def get_section(id):
	section = Section.query.get_or_404(id)
	return jsonify(section.to_long_json())