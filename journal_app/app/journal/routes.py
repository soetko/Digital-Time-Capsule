from flask import Flask, request, redirect, current_app, render_template, flash, url_for, abort, send_from_directory
from config import Config
from flask_login import current_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from app import db
import sqlalchemy as sa 
from app.models import User, JournalEntry, Media, Tag, JournalEntryTag, JournalEntryMedia
from app.journal.forms import JournalEntryForm, EditJournalEntryForm
from app.journal import bp
import datetime as dt
import pandas as pd
from werkzeug.utils import secure_filename
from pathlib import Path
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
import datetime as dt
import pandas as pd
import json
from app.tags_generation.tags_generation import tags_generator


""" Route for displaying a user's journal entries. This also passes
    journal entry ids to the edit hyperlink allowing for a signed in
    user to edit an existing journal entry. Currently shows all 
    user journal entries in one page, which can be cumbersome.
    TODO: Add pagination, let user select how many entries to 
    show at one time.
"""
@bp.route('/journal/', methods=['GET', 'POST'])
@login_required
def journal():

    # Checks if user has created their first journal entry
    # this helps prevent errors when trying to display a journal page
    # with no journal entries
    test_entry_exists()
    
    entries = JournalEntry.query.filter_by(user_id=current_user.user_id).order_by(JournalEntry.entry_published.desc()).all()

    journal_entries = []
    for entry in entries:
        tags = [tag.tag_name for tag in entry.tags]
        journal_entry = {}
        the_key = str(entry.entry_id)

        journal_entry[the_key] = {
            'title': entry.entry_title,
            'date': pd.to_datetime(entry.entry_published),
            'image_path': ['blank', entry.media_id][0 if entry.media_id is None else 1],
            'content': entry.entry_body,
            'tags': tags.copy()
        }
        #flash(tags_generator(entry.entry_body))
        if journal_entry[the_key]['image_path'] != 'blank':
            media_file_info = db.first_or_404(sa.select(Media).where(Media.media_id == entry.media_id))
                    
            if media_file_info.media_format in ['jpg', 'png', 'gif', '.jpg', '.png', '.gif']:

                journal_entry[the_key]['image_path'] = media_file_info.media_file_path


        journal_entries.append(journal_entry.copy())

    if len(journal_entries) == 0:
        journal_entries.append({'one':{'title': 'your title here', 'date': 'when created?', 'content': 'what would you write?'}})
        journal_entries.append({'two':{'title': 'your title here', 'date': 'when created?', 'content': 'what would you write?'}})
        flash('You have no journal entries yet! Perhaps you should create one now..')

    return render_template('journal/journal.html', journal_entries=journal_entries)



""" Route for new journal entry. Title, Body, File attachment, and 
    Tag generation of body supported. Audio transcription implementation
    did not make it into this version due to current interface constraints.
    Tag field supports user entered tags or auto generated tags. Currently,
    user can add tag generations without using the zero shot tagging 
    functionality, or add them into addition to auto Tag generation.
    TODO (both new and edit): Markup implementaiton for journal entries,
    allowing for HTML / CSS element rendering (bold, italics, font, color, etc.)
"""
@bp.route('/new_entry', methods=['GET', 'POST'])
@login_required
def new_entry():
    form = JournalEntryForm()

    if request.method == 'POST' and form.validate_on_submit():
        new_entry = JournalEntry(
            user_id = current_user.user_id,            
            entry_title=form.title.data,
            media_id=None,
            entry_body=form.content.data
        )
        
        db.session.add(new_entry)
        db.session.flush()

        tags_str = form.tags.data
        new_entry.tags = list()
        my_tags = list()
        if tags_str:
            tags_list = [tag.strip() for tag in tags_str.split(',')]
            for tag_name in tags_list:
                if tag_name:
                    tag = db.session.scalar(sa.select(Tag).where(Tag.tag_name == tag_name))
                    if not tag:
                        tag = Tag(tag_name=tag_name)
                        db.session.add(tag)
                        db.session.commit()
                    new_entry.tags.append(tag)

        db.session.add(new_entry)
        db.session.commit()


        file = request.files['media_file']
        if file.filename != '':
            if upload_file(file, new_entry) is None:
                flash("it's none")
                return render_template('journal/new_entry.html', form=form)

        
        return redirect(url_for('journal.journal'))    
    else:
        return render_template('journal/new_entry.html', form=form)


def test_entry_exists():
    tst = JournalEntry.query.filter_by(user_id=current_user.user_id).first_or_404()
    if tst.entry_id is None:
        flash('no entries yet!')
        return(render_template('/index.html'))

""" Route to handle auto-Tag generation duties """
@bp.route('/generate_entry_tags', methods=['POST'])
@login_required
def generate_entry_tags():
    data = request.get_json()
    content = data.get('content', '')
    generated_tags = tags_generator(content)
    return json.dumps({'tags': generated_tags})


""" Handles uploading files. Uploaded files permitted include
    jpg, jpeg, png, gif, mp4, mp3, and avi. There is currently 
    a 32MB file size cap. Files are stored by username (directory).
    Further refinements should include purging old files no longer
    displayed or linked to a user's journal entry. File attribute
    checking (same filename, different files) are in the queue to
    implement. This route also utilized secure_filename checking
    to make shell injections more difficult.
"""
@bp.route('/new_entry', methods=['POST'])
@login_required
def upload_file(f_path, jrnl_entry, new_entry=True):
    filename = secure_filename(f_path.filename)
    filename = filename.lower()
    if filename != '':
        
        ### organize directories
        target_dir = 'app/static/uploads/{}'.format(current_user.username)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        
        file_ext = os.path.splitext(filename)[1]
        
        # NEED TO UPDATE THIS AND NEW_ENTRY?
        if file_ext not in current_app.config['ALLOWED_EXTENSIONS']:
            flash('{}: file type unsupported'.format(file_ext))
            return None

        elif new_entry:
            mf_path  = os.path.join(target_dir, filename)

            new_media_item = Media(
                media_file_path = mf_path,
                media_format = file_ext
            )

            f_path.save(mf_path)

            db.session.add(new_media_item)
            db.session.commit()

            db.session.add(jrnl_entry)
            jrnl_entry.media_id = new_media_item.media_id
            db.session.commit()
            return 0
        
        else:
            mf_path  = os.path.join(target_dir, filename)
            f_path.save(mf_path)

            return mf_path


""" Edit entry supports changing the title, body, image, or tags of 
    a post that has already been submitted. Edit entry essentially has
    all of the functionality of new journal entries, just over the top
    of an existing journal entry.
    
    It isn't possible to show anything other than 'No File Chosen' in the form field.
    Options to demosntrate there is a file there:
        1. Include a thumbnail under the Choose FileField
        2. Display text with the filename below it
        3. ??
"""
@bp.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id=None, media_id=None):    
    form = EditJournalEntryForm(enctype="multipart/form-data")
    m_id = None
    upload_success = False
    
    if request.method == 'POST' and form.validate_on_submit():
        upd_entry = db.first_or_404(sa.select(JournalEntry)
            .where(JournalEntry.entry_id == entry_id and JournalEntry.user_id == current_user.user_id))


        upd_entry.entry_title=form.title.data
        upd_entry.entry_body=form.content.data
        db.session.add(upd_entry)
        db.session.commit()
          
        tags_str = form.tags.data
        if tags_str:
            new_tags = list()
            tags_list = [tag.strip() for tag in tags_str.split(',')]
            for tag_name in tags_list:
                if tag_name:
                    tag = db.session.scalar(sa.select(Tag).distinct().where(Tag.tag_name == tag_name))
                    if not tag:
                        tag = Tag(tag_name=tag_name)
                        db.session.add(tag)
                        db.session.commit()
                    if tag_name is not None and tag is not '':
                        new_tags.append(tag)
     
            upd_entry = db.first_or_404(sa.select(JournalEntry)
                 .where(JournalEntry.entry_id == entry_id and JournalEntry.user_id == current_user.user_id))  
            upd_entry.tags = []
            for t in new_tags:
                upd_entry.tags.append(t)
            db.session.commit()


        if upd_entry.media_id is not None:
            m_id = db.first_or_404(sa.select(Media).where(Media.media_id == upd_entry.media_id))


        file = request.files['media_file']
        if file.filename != '':
            if m_id is not None:
                og_fpath = m_id.media_file_path
                og_fname = og_fpath.split('/')[-1]

                if og_fname != file.filename:
                    new_file = upload_file(file, upd_entry, False)
                    if new_file is None:
                        flash("it's none")
                        return render_template('journal/edit_entry.html', form=form)
                    else:
                        m_id = db.first_or_404(sa.select(Media).where(Media.media_id == upd_entry.media_id))
                        file_ext = os.path.splitext(new_file.split('/')[-1])[1]
                        m_id.media_format = file_ext
                        m_id.media_file_path = new_file
                        db.session.add(m_id)
                        db.session.commit()

                else:
                    # filename is the same as stored, do nothing
                    # TODO: check file attributes in case name is same but file is different
                    pass
            else: # Previously, there was no media file

                new_file = upload_file(file, upd_entry, False)
                if new_file is None:

                    return render_template('journal/edit_entry.html', form=form)
                else:
                    #flash(new_file)
                    new_media = Media(
                        media_file_path = new_file,
                        media_format = os.path.splitext(new_file.split('/')[-1])[1]
                    )   
                    db.session.add(new_media)
                    db.session.commit()
                    media_id = new_media.media_id
                    #m_id = new_media.copy()
                    upd_entry = db.first_or_404(sa.select(JournalEntry)
                        .where(JournalEntry.entry_id == entry_id and JournalEntry.user_id == current_user.user_id))
                    upd_entry.media_id = new_media.media_id # media_id back populates after commit

                    db.session.add(upd_entry)
                    db.session.commit()
                    return redirect(url_for('journal.journal')) 
        else:
            # no filename, but maybe that means no file attached?
            # TODO: Delete row? Replace with 1 pixel image?
            pass
        
        # if upd_entry is not None and m_id is None and media_id is None:
        #     upd_entry.entry_body=form.content.data#.replace('\n', '<br/>')
        #     db.session.add(upd_entry)
        #     db.session.commit()
            
        return redirect(url_for('journal.journal'))    

    
    if request.method == 'GET':  
        # information is already in form as its edit_entry
        if entry_id is not None:
            entry = db.first_or_404(sa.select(JournalEntry)
                .where(JournalEntry.entry_id == entry_id and JournalEntry.user_id == current_user.user_id))
            form.title.data = entry.entry_title
            form.content.data = entry.entry_body
            if entry.tags:
                form.tags.data = ', '.join([tag.tag_name for tag in entry.tags])
            media_id = entry.media_id
            
    else:
        "Probably better to redirect"
        pass

    return render_template('/journal/edit_entry.html', title='Edit Journal Entry', form=form, entry_id=entry_id, media_id=media_id)
