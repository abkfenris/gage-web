from flask import request, redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.geoa import ModelView as _ModelView
from flask_admin.base import MenuLink
from flask_admin.model import InlineFormAdmin
from flask_admin.contrib.fileadmin import FileAdmin as _FileAdmin
from flask_security import (roles_required,
                            current_user)

import logging
import os.path as op

from ..database import db
from ..models import User, Region, River, Section, Gage, Sensor, Correlation

path = op.join(op.dirname(__file__), '../static/images')

h_w = {'data-height': 400, 'data-width': 600}

logger = logging.getLogger(__name__)


class ModelView(_ModelView):
    #def is_accessible(self):
    #    auth = current_user.is_authenticated
    #    logger.error('ModelView is accessible. Auth=', auth)
    #    return auth

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


class FileAdmin(_FileAdmin):
    #def is_accessible(self):
    #    auth = current_user.is_authenticated
    #    logger.error('FileAdmin is accessible. Auth=', auth)
    #    return auth

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


class UserView(ModelView):
    def is_accessible(self):
        """
        Only allow admins to see other users
        """
        logger.error('Userview', current_user)
        return current_user.has_role('admin')


class CorrelationInlineView(InlineFormAdmin):
    pass


class SectionView(ModelView):
    column_list = ('name', 'path', 'slug', 'river', 'location')
    column_labels = dict(slug='URL Slug')
    column_searchable_list = ('name', River.name)
    form_widget_args = {'putin': h_w,
                        'takeout': h_w,
                        'path': h_w}
    #inline_models = (Correlation,)


class GageView(ModelView):
    can_create = True
    column_exclude_list = ('key',
                           'elevationUnits',
                           'zipcode',
                           'visible',
                           'elevation',
                           'backend_notes',
                           'description',
                           'short_description',
                           'started',
                           'ended')
    column_labels = dict(slug='URL Slug')
    column_searchable_list = ('name',
                              River.name,
                              'slug',
                              'local_town',
                              'location')
    # inline_models = (Sensor,)
    form_widget_args = {'point': h_w}


class SensorView(ModelView):
    form_excluded_columns = ['samples']


class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        #if not current_user.is_authenticated:
        #    return redirect(url_for('security.login', next=request.url))
        return super(MyAdminIndexView, self).index()


class AuthenticatedMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


admin = Admin(name="Riverflo.ws",
              index_view=MyAdminIndexView(),
              template_mode='bootstrap3',
              )
admin.add_view(UserView(User, db.session))
admin.add_view(ModelView(Region, db.session))
admin.add_view(ModelView(River, db.session))
admin.add_view(SectionView(Section, db.session))
admin.add_view(GageView(Gage, db.session))
admin.add_view(SensorView(Sensor, db.session))
admin.add_view(ModelView(Correlation, db.session))
admin.add_view(FileAdmin(path, '/static/images/', name='Images'))
admin.add_link(AuthenticatedMenuLink(name='Logout',
                                     endpoint='security.logout'))
