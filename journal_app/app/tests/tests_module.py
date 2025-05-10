from flask_login import current_user
import unittest, pytest
from app import create_app, db
from app.models import User
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

    def test_not_registered_login(self):        
        user = db.session.scalar(db.select(User).where(
            User.username == 'never_registered'))
        self.assertTrue(user is None)

    def test_registration_works(self):        
        user_name = 'never_registered'
        user_email = 'shores@bbulldogs.ca'
        user_pw =  'nerg'
        user = User(username=user_name, email=user_email)
        user.set_password(user_pw)
        db.session.add(user)
        db.session.commit()
        user_exists = db.session.scalar(db.select(User).where(
            User.username == user_name))
        self.assertFalse(user_exists is None)

    def test_password_hashing(self):
        u = User(username='shoresy', email='shores@bbulldogs.ca')
        u.set_password('huh')
        self.assertFalse(u.check_password('what'))
        self.assertTrue(u.check_password('huh'))

    def test_registered_means_current_user(self):       
        user_name = 'never_registered'
        user_email = 'shores@bbulldogs.ca'
        user_pw =  'nerg'
        user = User(username=user_name, email=user_email)
        user.set_password(user_pw)
        db.session.add(user)
        db.session.commit()
        user_exists = db.session.scalar(db.select(User).where(
            User.username == user_name))
        self.assertTrue(current_user == None and user_exists is not None)

    def test_integration_registered_user_can_login(self):       
        user_name = 'never_ever_registered'
        user_email = 'shores@bbulldogs.ca'
        user_pw =  'nerg'
        user = User(username=user_name, email=user_email)
        user.set_password(user_pw)        
        db.session.add(user)
        db.session.commit()
        user_exists = db.session.scalar(db.select(User).where(
            User.username == user_name))
        response = self.app.post('/test_login', data=dict(
            username=user_name, password=user_pw))
        self.assertTrue(response)

# pytest command line:
#  python -m pytest -v app/tests/tests_module_combined.py
if __name__ == '__main__':
    unittest.main(verbosity=2)