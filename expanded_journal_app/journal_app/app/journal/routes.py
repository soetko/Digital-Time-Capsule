from flask import Flask, request, redirect, current_app, render_template, flash, url_for
from config import Config
from flask_login import current_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from app import db
import sqlalchemy as sa 
from app.models import User, JournalEntry
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
        journal_entry = {}
        journal_entry[str(entry.entry_id)] = {
            'title': entry.journal_title,
            'date': pd.to_datetime(entry.entry_published).strftime('%B %d, %Y at %H:%M GMT'),
            'content': entry.journal_entry
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
            user_id = current_user.user_id,            
            journal_title=form.title.data, 
            # media tbd
            journal_entry=form.content.data)
        db.session.add(new_entry)
        db.session.commit()
        flash('New entry created.')
        return render_template(url_for('journal.new_entry'))    
    return render_template('journal/new_entry.html', form=form)

#@bp.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
@bp.route('/edit_entry')
@bp.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id=None):    
    form = EditJournalEntryForm()
    if entry_id is not None:
        entry = db.first_or_404(sa.select(JournalEntry)
            .where(JournalEntry.entry_id == entry_id and JournalEntry.user_id == current_user.user_id))


    if request.method == 'POST' and form.validate_on_submit():        
        entry.journal_title = request.form['title']
        db.session.commit()
        entry.journal_entry = request.form['content']
        db.session.commit()
        
        flash('Journal entry updated.')
        return redirect(url_for('journal.journal'))

    elif request.method == 'GET':
        form.title.data = entry.journal_title
        form.content.data = entry.journal_entry
    return render_template('/journal/edit_entry.html', title='Cool', form=form, entry_id=entry_id)
