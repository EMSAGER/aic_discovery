#tests artwork.py
#tests the code that saves artwork to the db or to a file

from unittest import TestCase
from models import User, Artist, Artwork, Classification, Favorite, NotFavorite, Century, connect_db, db
import os

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_models_user.py


#set up the environmenta database

os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

#import the app
from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

class ModelsViewTestCase(TestCase):
    """Tests for user related routes"""
    def setUp(self):
        """Create test client add sample data"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()  
        db.create_all()
        self.cleardb()
        self.century_seed()

    def cleardb(self):
        User.query.delete()
        Artwork.query.delete()
        Artist.query.delete()
        Favorite.query.delete()
        Century.query.delete()

    def century_seed(self):
        c_18 = Century(century_name="18th Century")
        db.session.add(c_18)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """test the User Model"""
        user = User.signup("testuser2", "password", "test2@example.com", "Test", "User", c_18.id)
        self.assertIsNotNone(user.id)
