from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.user_settings import bp
from app.user_settings.forms import EditProfileForm, EditEmailForm, ChangePasswordForm
import sqlalchemy as sa
from app.models import User
from werkzeug.security import generate_password_hash

@bp.before_request
@login_required
def before_request():
    pass

@bp.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(('Your profile has been updated.'))
        return redirect(url_for('user_settings.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('user_settings/edit_profile.html', title=('Edit Profile'), form=form)

@bp.route('/email', methods=['GET', 'POST'])
def edit_email():
    form = EditEmailForm(current_user.email)
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash(('Your email address has been updated.'))
        return redirect(url_for('user_settings.edit_email'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('user_settings/edit_email.html', title=('Change Email'), form=form)

@bp.route('/password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        if current_user.check_password(current_password):
            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash(('Your password has been changed successfully.'))
            return redirect(url_for('user_settings.change_password'))
        else:
            flash(('Incorrect current password.'))
    return render_template('user_settings/change_password.html', title=('Change Password'), form=form)