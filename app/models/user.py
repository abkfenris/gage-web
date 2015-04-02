"""
Model for user
"""
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(db.Model):
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
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable atribute')

    @password.setter
    def password(self, password):
        """
        Takes user generated password and uses werkzeug.security to create a
        hash and stores it.
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Verify's user's password against stored werkzeug.security hash.

        Arguments:
            password (str): password to check against stored hash
        """
        return check_password_hash(self.password_hash, password)

    # def __init__(self, username, email):
    #     self.username = username
    #     self.email = email

    def __repr__(self):
        return '<User %r>' % self.username
