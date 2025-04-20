from flask import Flask
from flask_migrate import Migrate
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import LoginManager

from config import Config
from app import db
from app.models import User, JournalEntry

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

migrate = Migrate(app, db)

from app import route, errors

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': JournalEntry}
