from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, current_app, send_from_directory
from flask_login import current_user, login_required, LoginManager
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm
from app.models import User, JournalEntry, Media, Tag
from app.main import bp
import os

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/') 
@bp.route('/index') 
@login_required
def index():
    # journal_entries = [
    #     {
    #         'author': {'username': 'Clark'},
    #         'journal_title': {'journal_title'},
    #         'journal_entry': {'a body !'},
    #         'journal_entry_date': {'journal_entry.date'}
    #     },
    #     {
    #         'author': {'username': 'Clark!'},
    #         'journal_title': {'username': 'Clark?'},
    #         'journal_entries': {'title:a body !!'},
    #         'journal_entry_date': {'journal_entry.date'}
    #     }
    # ]
    return render_template('index.html')#, title=journal_entries, journal_entries=journal_entries)


@bp.route('/user/<username>')
@login_required
def user(username):
    # if current_user.user_id == username:
    #     user = db.first_or_404(sa.select(User).where(User.username == username))
    #     journal_entries = [
    #         {'author': user, 'body': 'follow up on this'},
    #         {'author': user, 'body': 'share this with cousin Betty'}
    #     ]
    #     return render_template('user.html', user=user, journal_entries=journal_entries)
    # else:
    #     flash(('No peeking!!'))
    return redirect(url_for('main.index'))


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        #current_user.about_me = form.about_me.data
        db.session.commit()
        flash(('Your changes have been saved.'))
        return redirect(url_for('user_settings.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        #form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=('Edit Profile'), form=form)


