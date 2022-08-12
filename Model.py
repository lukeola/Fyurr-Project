
# from flask_migrate import Migrate
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import ARRAY
# db = SQLAlchemy()

# def db_setup(app):
#     db.app = app
#     db.init_app(app)
#     Migrate(app,db)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from flask_migrate import Migrate


app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)

# from app import db



class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500), nullable = False)
    genres = db.Column(db.JSON, nullable=False, default=[])
    shows = db.relationship('Show', backref='venue', lazy=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120),  nullable=False)
    phone = db.Column(db.String(120),  nullable=False)
    genres = db.Column(db.JSON,  nullable=False, default=[])
    image_link = db.Column(db.String(500),  nullable=False)
    facebook_link = db.Column(db.String(120),  nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500), nullable = False)
    shows = db.relationship('Show', backref='artist', lazy=False)


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

