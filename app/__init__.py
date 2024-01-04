from flask import Flask
from config import Config
from flask_login import LoginManager
from app.models import db, User  
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

try:
    import spotipy
except ImportError:
    spotipy = None

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)
migrate = Migrate(app, db)

from app import routes
