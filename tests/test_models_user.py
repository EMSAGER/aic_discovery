#tests model.py
#tests the User Model

from unittest import TestCase
from models import User, Artist, Artwork, Favorite, Century, db
import os
import logging


# Set up logging
logging.basicConfig(level=logging.WARNING)  # Set to WARNING to reduce output, or ERROR to make it even less verbose

# Adjust logging level for SQLAlchemy specifically if needed
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

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

        self.username = "testuser"
        self.email = "test@test.com"

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

    def test_user_signup(self):
        """Test user signup."""
        user = User.signup(username="testuser", password="password", email="test@test.com", 
                           first_name="Test", last_name="User", century_id=self.century.id)
        db.session.commit()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.password.startswith("$2b$"))

    def test_user_signup_duplicate_username(self):
        """Test to prevent duplicate username signup."""
        User.signup(username=self.username, password="password", email=self.email,
                    first_name="Test", last_name="User", century_id=self.century.id)
        db.session.commit()

        # Expecting the duplicate signup to raise a ValueError
        with self.assertRaises(ValueError) as context:
            User.signup(username=self.username, password="password2", email="test2@test.com",
                        first_name="Test2", last_name="User2", century_id=self.century.id)
            db.session.commit()
        
        self.assertTrue('Username already exists' in str(context.exception))

    def test_user_authenticate_success(self):
        """Test successful user authentication."""
        user = User.signup(username="authuser", password="password", email="auth@test.com",
                           first_name="Auth", last_name="User", century_id=self.century.id)
        db.session.commit()
        authenticated_user = User.authenticate(username="authuser", pwd="password")
        self.assertEqual(user.id, authenticated_user.id)

    def test_user_authenticate_wrong_password(self):
        """Test user authentication with wrong password."""
        User.signup(username="authuser", password="password", email="auth@test.com",
                    first_name="Auth", last_name="User", century_id=self.century.id)
        db.session.commit()
        authenticated_user = User.authenticate(username="authuser", pwd="wrongpassword")
        self.assertFalse(authenticated_user)

    def test_user_authenticate_nonexistent_user(self):
        """Test authentication with nonexistent user."""
        authenticated_user = User.authenticate(username="nobody", pwd="password")
        self.assertFalse(authenticated_user)

    def test_full_name(self):
        """Test the full name property."""
        user = User.signup(username="fullnameuser", password="password", email="fullname@test.com",
                           first_name="Full", last_name="Name", century_id=self.century.id)
        db.session.commit()
        self.assertEqual(user.full_name, "Full Name")
