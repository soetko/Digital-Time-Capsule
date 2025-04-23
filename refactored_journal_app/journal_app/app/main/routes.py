from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm
from app.models import User, JournalEntry
from app.main import bp



@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/') 
@bp.route('/index') 
@login_required
def index():
    entries = [
        {
            'author': {'username': 'Clark'},
            'journal_title': "Thoughts",
            'body': "I thought about this and did that other thing then stopped."
        },
        {
            'author': {'username': 'Clark'},
            'journal_title': "Words",
            'body': "More words all the time sometimes they even make sense"
        }
    ]
    return render_template('index.html', title='Journal Home', entries=entries)




@bp.route('/user/<username>')
@login_required
def user(username):
    if current_user.id == username:
        user = db.first_or_404(sa.select(User).where(User.username == username))
        entries = [
            {'author': user, 'body': 'follow up on this'},
            {'author': user, 'body': 'share this with cousin Betty'}
        ]
        return render_template('user.html', user=user, entries=entries)
    else:
        flash(('No peeking!!'))
        return redirect(url_for('main.index'))




@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=('Edit Profile'), form=form)
