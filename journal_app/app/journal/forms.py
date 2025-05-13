from datetime import datetime, timezone
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, JournalEntry, JournalEntryTag, Tag, Media
from app.journal import bp

""" Journal Forms - currently the same for edit and new journal entry """
class JournalEntryForm(FlaskForm):
    title = StringField(('Title'), validators=[DataRequired()])
    media_file = FileField('Media File', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'mp4'])])
    content = TextAreaField('Content', validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)')#, render_kw={'readonly': True})
    submit = SubmitField('Save')

class EditJournalEntryForm(FlaskForm):
    title = StringField(('Title'), validators=[DataRequired()])
    media_file = FileField()
    content = TextAreaField('Content', validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)')#, render_kw={'readonly': True})
    submit = SubmitField('Save')
