"""
When things go wrong sitewide they are handled by the app_errorhandlers
"""
from flask import render_template, request, jsonify, current_app
from flask_security.core import current_user

from .blueprint import main
from ..models import Gage


@main.app_errorhandler(403)
def forbidden(e):
    """
    Handle 403 Forbidden errors in html and json
    """
    current_app.logger.error('{} got a 403 Forbidden error trying to access {}. {}'.format(
        getattr(current_user, 'email', 'Anonymous'),
        request.url,
        e
    ))
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html', Gage=Gage), 403


@main.app_errorhandler(404)
def page_not_found(e):
    """
    Handle 404 Page Not Found errors in html and json
    """
    current_app.logger.error('{} got a 404 Page Not Found trying to access {}. {}'.format(
        getattr(current_user, 'email', 'Anonymous'),
        request.url,
        e
    ))
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html', Gage=Gage), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    """
    Handle 500 Internal Server errors in html and json
    """
    current_app.logger.error('{} got a 500 Internal Server Error trying to access {}. {}'.format(
        getattr(current_user, 'email', 'Anonymous'),
        request.url,
        e
    ))
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html', Gage=Gage), 500
