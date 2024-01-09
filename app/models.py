from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    spotify_id = db.Column(db.String, unique=True, nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow())
    songs = db.relationship('Song', backref='user', lazy=True)


    def __init__(self, username, spotify_id=None):
        self.username = username
        self.spotify_id = spotify_id


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    feelings = db.Column(db.Text, nullable=True)  # Add this line for the 'feelings' field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, title, artist, rating, description, feelings, user_id):
        self.title = title
        self.artist = artist
        self.rating = rating
        self.description = description
        self.feelings = feelings
        self.user_id = user_id

