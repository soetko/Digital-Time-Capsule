from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, current_app, send_from_directory
from flask_login import current_user, login_required, LoginManager
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm
from app.models import User, JournalEntry, Media, Tag
from app.main import bp
import os

""" Main page related routes """

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/') 
@bp.route('/index') 
@login_required
def index():
    return render_template('index.html')

@bp.route('/user/<username>')
@login_required
def user(username):
    return redirect(url_for('main.index'))



