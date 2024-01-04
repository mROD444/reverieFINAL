from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    spotify_id = db.Column(db.String, unique=True, nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow())


    def __init__(self, username, spotify_id=None):
        self.username = username
        self.spotify_id = spotify_id
