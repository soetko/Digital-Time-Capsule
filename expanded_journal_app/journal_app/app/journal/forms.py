from datetime import datetime, timezone
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, JournalEntry, JournalEntryTag, Tag
from app.journal import bp

class JournalEntryForm(FlaskForm):
    title = StringField(('Title'), validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)')
    save_draft = SubmitField('Save Draft')
    submit = SubmitField('Save')

class EditJournalEntryForm(FlaskForm):
    title = StringField(('Title'), validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    tags = StringField('Tags (comma-separated)')
    submit = SubmitField('Save')