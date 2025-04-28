from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField(('New Username'), validators=[DataRequired(), Length(min=1, max=64)])
    about_me = TextAreaField(('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(('Save Profile'))

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None:
                raise ValidationError(('This username is already taken.'))

class EditEmailForm(FlaskForm):
    email = StringField(('New Email'), validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField(('Change Email'))

    def __init__(self, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = db.session.scalar(sa.select(User).where(User.email == email.data))
            if user is not None:
                raise ValidationError(('This email address is already in use.'))

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(('Current Password'), validators=[DataRequired()])
    new_password = PasswordField(('New Password'), validators=[DataRequired()])
    new_password2 = PasswordField(
        ('Repeat New Password'), validators=[DataRequired(), EqualTo('new_password')]
    )
    submit = SubmitField(('Change Password'))

    def validate_current_password(self, current_password):
        user = db.session.scalar(sa.select(User).where(User.id == current_user.id))
        if user is None or not user.check_password(current_password.data):
            raise ValidationError(('Incorrect current password.'))