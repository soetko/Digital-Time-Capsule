from flask import Flask, request, redirect, current_app, render_template, flash, url_for, abort
from config import Config
from flask_login import current_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from app import db
import sqlalchemy as sa 
from app.models import User, JournalEntry, Tag
from app.journal.forms import JournalEntryForm, EditJournalEntryForm
from app.journal import bp
import datetime as dt
import pandas as pd


@bp.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    entries = JournalEntry.query.filter_by(user_id=current_user.user_id).order_by(JournalEntry.entry_published.desc()).all()
    
    journal_entries = []
    for entry in entries:
        tags = [tag.tag_name for tag in entry.tags]
        journal_entry = {}
        journal_entry[str(entry.entry_id)] = {
            'title': entry.journal_title,
            'date': pd.to_datetime(entry.entry_published).strftime('%B %d, %Y at %H:%M GMT'),
            'content': entry.journal_entry,
            'tags': tags
        }
        
        journal_entries.append(journal_entry.copy())
        
    if len(journal_entries) == 0:
        journal_entries.append({'one':{'title': 'your title here', 'date': 'when created?', 'content': 'what would you write?'}})
        journal_entries.append({'two':{'title': 'your title here', 'date': 'when created?', 'content': 'what would you write?'}})
        flash('You have no journal entries yet! Perhaps you should create one now..')

    return render_template('journal/journal.html', journal_entries=journal_entries)

@bp.route('/new_entry', methods=['GET', 'POST'])
@login_required
def new_entry():
    form = JournalEntryForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_entry = JournalEntry(
            user_id=current_user.user_id,
            journal_title=form.title.data,
            journal_entry=form.content.data
        )
        db.session.add(new_entry)
        db.session.flush()  # To get the new_entry.entry_id immediately

        tags_str = form.tags.data
        if tags_str:
            tags_list = [tag.strip() for tag in tags_str.split(',')]
            for tag_name in tags_list:
                if tag_name:
                    tag = db.session.scalar(sa.select(Tag).where(Tag.tag_name == tag_name))
                    if not tag:
                        tag = Tag(tag_name=tag_name)
                        db.session.add(tag)
                    new_entry.tags.append(tag)

        db.session.commit()
        flash('New entry created.')
        return redirect(url_for('journal.journal'))
    return render_template('journal/new_entry.html', form=form)

@bp.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    stmt = sa.select(JournalEntry).where(JournalEntry.entry_id == entry_id, JournalEntry.user_id == current_user.user_id)
    entry = db.session.execute(stmt).scalar_one_or_none()
    if entry is None:
        abort(404)
    form = EditJournalEntryForm(obj=entry) # Initialize form with entry data

    if request.method == 'POST' and form.validate_on_submit():
        entry.journal_title = form.title.data
        entry.journal_entry = form.content.data

        # Process tags
        new_tags_str = form.tags.data
        new_tags = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]

        # Clear existing tags
        entry.tags = []

        # Add the new tags
        for tag_name in new_tags:
            tag = db.session.scalar(sa.select(Tag).where(Tag.tag_name == tag_name))
            if not tag:
                tag = Tag(tag_name=tag_name)
                db.session.add(tag)
            entry.tags.append(tag)

        db.session.commit()
        flash('Journal entry updated.')
        return redirect(url_for('journal.journal'))

    elif request.method == 'GET':
        form.title.data = entry.journal_title
        form.content.data = entry.journal_entry
        form.tags.data = ', '.join([tag.tag_name for tag in entry.tags])

    return render_template('/journal/edit_entry.html', title='Edit Entry', form=form, entry_id=entry_id)
