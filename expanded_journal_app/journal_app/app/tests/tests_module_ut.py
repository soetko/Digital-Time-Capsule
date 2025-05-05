from datetime import datetime, timezone, timedelta
import unittest, pytest
from app import create_app, db
from app.models import User, JournalEntry
from app.forms import LoginForm, RegisterForm
from config import Config




class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ELASTICSEARCH_URL = None


    


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_link_unauthenticated_user(self):
        register_form = RegisterForm(username='jim', password='jimmy')
        response = self.app.post("/register", data=register_form.data, follow_redirects=True)
        assert html_response.status_code == 200 


    def test_password_hashing(self):
        u = User(username='shoresy', email='shores@bbulldogs.ca')
        u.set_password('huh')
        self.assertFalse(u.check_password('what'))
        self.assertTrue(u.check_password('huh'))

if __name__ == '__main__':
    unittest.main(verbosity=2)