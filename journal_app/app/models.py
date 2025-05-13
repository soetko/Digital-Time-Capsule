from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from app import db, login
from hashlib import md5

""" Definition of classes / tables related to users and JournalEntries """
class User(UserMixin, db.Model):
    user_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    journal_entries: so.WriteOnlyMapped['JournalEntry'] = so.relationship(back_populates='author')
    last_login: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    def set_user_upload_directory(self):
        return 'journal/uploads/{}'.format(self)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_id(self):
        return self.user_id

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Media(db.Model):
    media_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    media_uploaded_date: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    media_format: so.Mapped[str] = so.mapped_column(sa.String(10))
    media_file_path: so.Mapped[str] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return '<Media {}>'.format(self.media_id)    


class JournalEntry(db.Model):
    entry_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.user_id), index=True)
    media_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Media.media_id), nullable=True)
    entry_title: so.Mapped[str] = so.mapped_column(sa.String(1024))
    entry_body: so.Mapped[str] = so.mapped_column(sa.String(64000))
    entry_published: so.Mapped[str] = so.mapped_column(default=lambda: datetime.now(timezone.utc), index=True)
    last_mod_date: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    author: so.Mapped[User] = so.relationship(back_populates='journal_entries')
    tags: so.Mapped[list['Tag']] = so.relationship(secondary='journal_entry_tag', backref=so.backref('journal_entries', lazy='dynamic'))

    def __repr__(self):
        return '<JournalEntry {}>'.format(self.entry_title)


class Tag(db.Model):
    tag_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    tag_name: so.Mapped[str] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return '<Tag {}>'.format(self.tag_name)


class JournalEntryTag(db.Model):
    entry_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(JournalEntry.entry_id), primary_key=True)
    tag_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Tag.tag_id), primary_key=True)

    def __repr__(self):
        return '<JournalEntryTag {}, {}>'.format(self.entry_id, self.tag_id)

""" Not currently used """
class JournalEntryMedia(db.Model):
    entry_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(JournalEntry.entry_id), primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.user_id), primary_key=True)
    media_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Media.media_id), primary_key=True)

    def __repr__(self):
        return '<JournalEntryMedia {}, {}, {}>'.format(self.entry_id, self.user_id, self.media_id)

