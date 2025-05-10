from flask import Flask, request, current_app, send_from_directory, url_for
from config import Config
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_bootstrap import Bootstrap5
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Log in required.'
bootstrap = Bootstrap5()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='./static')
    app.config.from_object(config_class)
    app.config['MEDIA_UPLOADS'] = './static/uploads/'
    app.config['ALLOWED_EXTENSIONS'] = [
        '.jpg', '.jpeg','.png', '.gif', '.mp4', '.avi', '.mp3', '.pdf',
        'jpg', 'gif', 'png', 'jpeg', 'mp4', 'avi', 'mp3', 'pdf'
    ]
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 # 32mb max file size
    bootstrap.init_app(app)    
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app) 

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.journal import bp as journal_bp
    app.register_blueprint(journal_bp, url_prefix='/journal')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/main')

    #from app import views

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/journal_app.log', maxBytes=10240,  backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Digital-Journal-App startup')

    return app

from app import models
