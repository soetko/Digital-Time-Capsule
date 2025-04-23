from datetime import datetime, timezone, timedelta
import unittest
from app import create_app, db
from app.models import User, JournalEntry
from config import Config
#from config.db import connect_db


def test_db_connection():
    @db.session()
    def create_connection(conn):
        assert conn is not None
    create_connection()