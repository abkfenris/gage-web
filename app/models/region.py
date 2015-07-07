"""
Region model
"""
from flask import url_for

from app.database import db


class Region(db.Model):
    """
    Regions where Rivers, Sections, and Gages exist

    Arguments:
        id (int): Primary Region Key
        name (str): Nice name
        slug (str): slug for url formatting
        description (text): Long description that can contain HTML or Markdown within reason.
        short_description (text): Short description, for showing on other pages.
        header_image (str): Header image to override default.
        rivers: List of ``River`` objects for Region.
        sections: List of ``Section`` objects for Region.
        gages: List of ``Gage`` objects for Region.
    """
    __tablename__ = 'regions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    slug = db.Column(db.String(80))
    description = db.Column(db.Text)
    short_description = db.Column(db.Text)
    header_image = db.Column(db.String(80))

    def to_json(self):
        """
        Create a JSON object from region. Used where multiple regions may be
        displayed simultaneously.
        """
        json_region = {
            'id': self.id,
            'name': self.name,
            'url': url_for('api.get_region', id=self.id, _external=True),
            'html': url_for('main.regionpage', slug=self.slug, _external=True),
        }
        return json_region

    def to_long_json(self):
        """
        Create a JSON object from region. Used when only one region is to be
        displayed.
        """
        json_region = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sections': [section.to_json() for section in self.sections],
            'gages': [gage.to_json() for gage in self.gages],
            'rivers': [river.to_json for river in self.rivers],
            'url': url_for('api.get_region', id=self.id, _external=True),
            'html': url_for('main.regionpage', slug=self.slug, _external=True)
        }
        return json_region

    def __repr__(self):
        return '<Region %r>' % self.name
