#tests model.py
#tests the User Model

from unittest import TestCase
from models import User, Artist, Artwork, Favorite, Century, db
import os

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_models_user.py


#set up the environmenta database

os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

#import the app
from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

class UserModelTestCase(TestCase):
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
        # Seed a Century instance for use in tests
        self.century = Century(century_name="21st Century")
        db.session.add(self.century)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """test the User Model"""
        user = User.signup(username="testuserzzzz", password="password", email="test@test.com", 
                           first_name="Test", last_name="User", century_id=self.century.id)
        self.assertIsNotNone(user)
    
    def test_user_authenticate(self):
        """Test user authentication."""
        self.test_user_creation()
        user = User.authenticate(username="testuserzzzz", pwd="password")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuserzzzz")

