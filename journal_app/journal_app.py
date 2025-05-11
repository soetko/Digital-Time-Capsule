import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import User, JournalEntry
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

app = create_app()

#auto-generate db
with app.app_context():
    db.drop_all()
    db.create_all()

#or destry all
# with app.app_context():
#     db.drop_all()
#     db.create_all()

@app.shell_context_processor
def make_shell_context():
    #return {'sa': sa, 'so': so, 'db': db, 'User': User, 'JournalEntry': JournalEntry, 'Tag':Tag, 'Media':Media}
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'JournalEntry': JournalEntry}