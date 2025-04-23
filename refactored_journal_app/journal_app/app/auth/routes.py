from flask import render_template, flash, redirect, url_for, request
from app import db
from app.auth.forms import LoginForm, RegistrationForm
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa 
from app.models import User
from datetime import datetime, timezone
from app.auth import bp

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(('Welcome to your digital Journal!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=('Register'), form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title=('Sign In'), form=form)

@bp.route('/test_login', methods=['GET', 'POST'])
def test_login():
    response = login_user(user, remember=form.remember_me.data)
    if response == True:
        return True
    else:
        return false

