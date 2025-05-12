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


### Seems like it should be easy, but not so much so far
## UPLOADS FOLDER by USER
## EDIT entry allow upload file change


#MEDIA_UPLOADS = 'uploads'
@bp.route('/journal/', methods=['GET', 'POST'], enctype="multipart/form-data")
@login_required
def journal():
    if not os.path.exists(User.set_user_upload_directory(current_user.username)):
        os.makedirs(User.set_user_upload_directory(current_user.username))
    entries = JournalEntry.query.filter_by(user_id=current_user.user_id).order_by(JournalEntry.entry_published.desc()).all()
    #media_files = Media.query.filter_by(user_id=current_user.user_id).order_by(Media.media_uploaded_date.dec()).all()
    #for x in entries:
    #    flash('{}-{}'.format(x.entry_id, x.media_id))

    ## maybe better to roll this into the user class


    journal_entries = []
    #media_files = {}
    for entry in entries:
        journal_entry = {}
        the_key = str(entry.entry_id)
        #flash(the_key)
        journal_entry[the_key] = {
            'title': entry.entry_title,
            'date': pd.to_datetime(entry.entry_published).strftime('%B %d, %Y at %H:%M GMT'),
            'image_name': ['blank', entry.media_id][0 if entry.media_id is None else 1],
            'content': entry.entry_body
        }
        #flash('!!{}'.format(['blank', entry.media_id][0 if entry.media_id is None else 1]))
        #flash(entry.media_id)
        #flash(current_app.config['MEDIA_UPLOADS'])
        # if entry.media_id is not None:
        #     entry_media_id = JournalEntryMedia.query.filter_by(
        #         user_id=current_user.user_id, 
        #         entry_id=entry.entry_id,
        #         media_id=entry_media_id).all()
        #if journal_entry[the_key]['image_name'] != 'blank':
        
        
        #flash('.-{}-.'.format(journal_entry[the_key]['image_name']))
        
        
            #media_file[entry.media_id] = {} 
        #if entry.entry_id is not None:
        #flash('-\n-'.format(journal_entry))
        if journal_entry[the_key]['image_name'] != 'blank':
            media_file_info = db.first_or_404(sa.select(Media).where(Media.media_id == entry.media_id))
                    
            #flash(media_file_info.media_id)
            #flash(media_file_info.media_format)
                    #flash('.-{}-{}-.'.format(media_file_info.media_file_path, media_file_info.media_format))
            if media_file_info.media_format == '.jpg' or media_file_info.media_format == '.jpeg':
                #flash(media_file_info.media_file_path.split('/')[-1])
                journal_entry[the_key]['image_name'] = media_file_info.media_file_path.split('/')[-1]
                #flash(current_app.config['MEDIA_UPLOADS'])
                #flash(journal_entry[the_key]['image_name'] )
                #flash(journal_entry)
                
                
                #media_files[entry.entry_id] = media_file_info.media_file_path
                #flash(media_file_info.media_id)
                #flash(media_file_info.media_file_path)
                #flash(os.path.join(current_app.config['MEDIA_UPLOADS'], 'nonstop_winter.jpg'))
                #media_files.append(media_file.copy())

        #flash(os.path.getsize(os.path.join('tmp', 'nonstop_winter.jpg')))
        journal_entries.append(journal_entry.copy())

    #flash(journal_entries) 
    if len(journal_entries) == 0:
        journal_entries.append({'one':{'title': 'your title here', 'date': 'when created?', 'content': 'what would you write?'}})
        journal_entries.append({'two':{'title': 'your title here', 'date': 'when created?', 'content': 'what would you write?'}})
        flash('You have no journal entries yet! Perhaps you should create one now..', 'info')

    #flash(journal_entries)
    return render_template('journal/journal.html', journal_entries=journal_entries)#render_template('journal/journal.html', journal_entries=journal_entries) #, media_files=media_files)

@bp.route('/upload_now/<filename>')
def upload_now(filename, methods=['POST']):
    #root = Path('.journal_app/')
    #folder_path = os.path.join(root, current_app.config['MEDIA_UPLOADS'])#root / 'static'
    folder_path = user_upload_dir#'journal/{}'.format(current_user.username)
    #folder_path = current_app.config['MEDIA_UPLOADS']
    return send_from_directory(
        #directory=current_app.config['MEDIA_UPLOADS'], 
        folder_path,
        filename)#,
        #as_attachment=True, 
        #mimetype='application/jpeg')


@bp.route('/new_entry', methods=['GET', 'POST'], enctype="multipart/form-data")
@login_required
def new_entry():
    if not os.path.exists(User.set_user_upload_directory(current_user.username)):
        os.makedirs(User.set_user_upload_directory(current_user.username))
    form = JournalEntryForm()

    if request.method == 'POST' and form.validate_on_submit():
        new_entry = JournalEntry(
            user_id = current_user.user_id,            
            entry_title=form.title.data.replace('\n', '<br/>'),
            media_id=None,
            entry_body=form.content.data
        )
        file = request.files['media_file']
        if file.filename != '':
            file = file.filename
            #flash('..{}..'.format(file.filename))
            #form.media_field.data.file]
            #f_name = secure_filename(file.filename)#.filename)
            #flash(file.filename)
            #flash(f_name)
            #flash(jsonify({"filename": file.filename, "url": "/static/uploads/" + file.filename}))
            #f_name = secure_filename(form.media_field.data.file.filename)
            #f_name = secure_filename(file.filename)
            #flash('oh - {}'.format(file))
            if upload_file(file, new_entry) is None:
                return render_template('journal/new_entry.html', form=form)#redirect(request.referrer, form=form)
        
        #format_contents = form.title.data

        
        
        db.session.add(new_entry)
        db.session.commit()
        flash('New entry created.')
        return redirect(url_for('journal.journal'))    
    else:
        return render_template('journal/new_entry.html', form=form)

@bp.route('/new_entry', methods=['POST'])
@login_required
def upload_file(f_path, jrnl_entry, new_entry=True):
    #uploaded_file = f_path#request.files['file']
    flash(f_path)
    filename = secure_filename(f_path.filename)
    filename = filename.lower()
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        # NEED TO UPDATE THIS AND NEW_ENTRY
        if file_ext not in current_app.config['ALLOWED_EXTENSIONS']:
            flash('{}: file type unsupported'.format(file_ext))
            return None#'{}: file type unsupported'.format(file_ext), 400
            #return redirect(request.referrer)
            # return redirect(url_for('journal.new_entry'))
            #abort(400)
        elif new_entry:
            # mf_path = os.path.join(current_app.config['MEDIA_UPLOADS'], current_user.get_id(), filename)
            #if not os.path.exists(os.path.join(MEDIA_UPLOADS, current_user.username)):
            #    os.makedirs(os.path.join(MEDIA_UPLOADS, current_user.username))
            
            mf_path = os.path.join(user_upload_dir, filename)
            #id_ = 0
            new_media_item = Media(
                media_file_path = mf_path,
                media_format = file_ext
            )

            f_path.save(mf_path)
            flash('File Uploaded Successfully!', 'success')

            db.session.add(new_media_item)
            db.session.commit()

            jrnl_entry.media_id = new_media_item.media_id
            db.session.commit()
        
        else:
            mf_path = os.path.join(user_upload_dir, filename)
            f_path.save(mf_path)
            flash('File Uploaded Successfully!', 'success')

    #else:
            return redirect(url_for('journal.new_entry'))


@bp.route('/edit_entry')
@bp.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'], enctype="multipart/form-data")
@login_required
def edit_entry(entry_id=None):    
    form = EditJournalEntryForm()
    tmp_mfp = None
    flash('1.{}'.format(entry_id))
    if entry_id is not None:
        entry = db.first_or_404(sa.select(JournalEntry)
            .where(JournalEntry.entry_id == entry_id and JournalEntry.user_id == current_user.user_id))
        
        mfi = db.first_or_404(sa.select(Media).where(Media.media_id == entry.media_id))
        #flash(mfi.media_file_path)
        flash(entry.entry_id)


    ## In progress on editing media files...
    #flash('p{}'.format(entry.media_id))
    if request.method == 'POST' and form.validate_on_submit():        
        entry.entry_title = request.form['title']
        db.session.commit()
        
        entry.entry_body = request.form['content'] 
        db.session.commit()

        return redirect(url_for('journal.journal'))
    elif False: 
        flash('it is none')

        ## Everything but file attachment is handled at this point (content, title)
        #flash('-{}[]'.format(str(request.files['media_file'])))
        
        #flash('{}++'.format(str(tmp_mfp)))
        
        if request.method == 'GET': ## Turning all this off for now
            tmp_mfp = request.files['media_file']
            if tmp_mfp.filename != '':
            #if not (tmp_mfp == '' or tmp_mfp is None):
                filename = tmp_mfp.filename
                flash('{}=-=-='.format(filename))
                tmfp_format = os.path.splitext(filename)[1].lower()
                tmfp_path = filename#filename.split('/')[-1].lower()
                
                if tmfp_format not in current_app.config['ALLOWED_EXTENSIONS']:
                    flash('disallowed file format: {}'.format(tmfp_format))
                    return render_template('journal/new_entry.html', form=form)

                ## REVISIT
                # elif os.path.getsize(tmfp_path) > current_app.config['MAX_CONTENT_LENGTH']:
                #     flash('filesize exceeds max limit of {} MB'.format(current_app.config['MAX_CONTENT_LENGTH']/1000000))
                #     return render_template('journal/new_entry.html', form=form)
            elif tmfp_path == None or tmfp_path == '':
                ## we're done
                #flash('!!')
                return redirect(url_for('journal.journal'))

            #the_key = entry.media_id
            flash('!{}!'.format(tmfp_path))
            #mfi = 'tmp'
            new_entry = 'tmp'
            #if entry[the_key]['image_name'] != '' and journal_entry[the_key]['image_name'] != 'BLANK' and journal_entry[the_key]['image_name'] is not None:
            if entry.media_id is not None:
                #mfi = db.first_or_404(sa.select(Media).where(Media.media_id == entry.media_id))
                #mfi = db.first_or_404(sa.select(Media).where(Media.media_id == entry.media_id))
                if mfi is None:
                    flash('it is none')
                flash('{}...'.format(mfi.media_id))
                flash(str(mfi.media_file_path))
            else:
                # new_media_item = Media(
                # media_file_path = tmfp_path,
                # media_format = tmfp_format
                # )
                # then done
                if upload_file(tmp_mfp, entry) is None:
                    return render_template('journal/new_entry.html', form=form)

            if mfi.media_file_path is None and tmp_mfp is None:            
                #flash('!!')
                return redirect(url_for('journal.journal'))
            
            elif mfi.media_file_path is not None and tmp_mfp is not None and mfi.media_file_path == tmp_mfp:
                #flash('!!')
                return redirect(url_for('journal.journal'))
                
            ## user changed file, update database
            elif mfi.media_file_path is not None and tmp_mfp is not None and mfi.media_file_path != tmp_mfp:
                #flash('!!')
                ## REVISIT ##
                #os.rename(mfi.media_file_path, '{}{}'.format(mfi.media_file_path, '.marked_for_deletion'))
                flash(tmfp_path)
                mfi.media_file_path = tmfp_path
                db.session.commit()

                mfi.media_format =  tmfp_format
                db.session.commit()

                ## Not a new entry, just uploading
                upload_file(tmp_mfp, None, False)

            
            elif mfi.media_file_path is None:
                #flash('!!')
                #if not os.path.exists(os.path.join(MEDIA_UPLOADS, current_user.username)):
                #    os.makedirs(os.path.join(MEDIA_UPLOADS, current_user.username))
                
                mfi.media_file_path = tmfp_path
                db.session.commit()

                mfi.media_format =  tmfp_format
                db.session.commit()

                ## Not a new entry, just uploading
                upload_file(tmp_mfp, None, False)

            else:
                flash('somehow we got here')

            #flash('!!')
            flash('Journal entry updated.')
            return redirect(url_for('journal.journal'))

    elif request.method == 'GET':
        #flash('!!')
        form.title.data = entry.entry_title
        #flash('{}'.format(['', entry.media_id][0 if entry.media_id is None else 1]))
        flash(str(tmp_mfp))
        form.media_file.data = tmp_mfp#['', entry.media_id][0 if entry.media_id is None else 1]
        form.content.data = entry.entry_body
    return render_template('/journal/edit_entry.html', title='Cool', form=form, entry_id=entry_id)
