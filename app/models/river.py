"""
River model
"""
from flask import url_for
from app import db

# many to many table to connect rivers to regions
rivers_regions = db.Table('rivers_regions',
    db.Column('river', db.Integer, db.ForeignKey('rivers.id')),
    db.Column('region', db.Integer, db.ForeignKey('regions.id'))
)


class River(db.Model):
    """
    River model. Rivers are rivers as we know them they have a parent that they
    flow downstream into and have tributaries that flow into them.

    Arguments:
        id (int): Primary River id
        name (string): Nice River name
        slug (string): slug for url formatting
        description (text): Long description that can contain HTML or Markdown within reason.
        short_description (text): Short description for showing on other pages.
        header_image (string): Header image to override default
        parent_id (int): River.id for the river that this one flows into
        parent: ``River`` object from parent_id
        tributary: List of ``River`` objects for any River that has this one in it's parent_id.
        regions: List of ``Region`` objects for River
        sections: List of ``Section`` objects for River
    """
    __tablename__ = 'rivers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    slug = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    short_description = db.Column(db.Text)
    header_image = db.Column(db.String(80))

    parent_id = db.Column(db.Integer, db.ForeignKey('rivers.id'))
    parent = db.relationship('River', remote_side=id, backref='tributary')

    regions = db.relationship('Region', secondary=rivers_regions,
                              backref=db.backref('rivers', lazy='dynamic'))

    #def __init__(self, name, slug, description,
    #            short_description, header_image, parent):
    #    self.name = name
    #    self.slug = slug
    #    self.description = description
    #    self.short_description = short_description
    #    self.header_image = header_image
    #    self.parent = parent

    def to_json(self):
        """
        Creates a JSON Object from River. Used where multiple rivers may be
        listed at once.
        """
        json_river = {
            'id': self.id,
            'name': self.name,
            'url': url_for('api.get_river', id=self.id, _external=True),
        }
        return json_river

    def to_long_json(self):
        """
        Creates a JSON Object from River. Used where a single river is being
        displayed.
        """
        if self.parent is not None:
            json_river = {
                'id': self.id,
                'name': self.name,
                'url': url_for('api.get_river', id=self.id, _external=True),
                'sections': [section.to_json() for section in self.sections],
                'downstream': self.parent.to_json(),
                'tributaries': [river.to_json() for river in self.tributary],
                'gages': [gage.to_json() for gage in self.gages]
            }
        else:
            json_river = {
                'id': self.id,
                'name': self.name,
                'url': url_for('api.get_river', id=self.id, _external=True),
                'sections': [section.to_json() for section in self.sections],
                'tributaries': [river.to_json() for river in self.tributary],
                'gages': [gage.to_json() for gage in self.gages]
            }
        return json_river

    def __repr__(self):
        return '<River %r>' % self.name
