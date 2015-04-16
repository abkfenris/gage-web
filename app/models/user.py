"""
Model for user
"""
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore

from app import db

roles_users = db.Table('roles_users',
                       db.Column('user_id',
                                 db.Integer(),
                                 db.ForeignKey('users.id')),
                       db.Column('role_id',
                                 db.Integer(),
                                 db.ForeignKey('roles.id')))


class Role(db.Model, RoleMixin):
    """
    Role Model

    Using Flask-Security's RoleMixin

    Arguments:
        id (int): Primary Role Key
        name (str): Role name for reference in admin and for restrictions
        description (str): Role description
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        if self.description is not None:
            return '{0} - {1}'.format(self.name, self.description)
        return '{0}'.format(self.name)


class User(db.Model, UserMixin):
    """
    User model

    Arguments:
        id (int): Primary User Key
        username (str): Unique username as chosen by the user
        email (str): User's email address
        password_hash (str): Users hashed password
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.username

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
