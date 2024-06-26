from unittest import TestCase
from unittest.mock import patch
from models import User, Century, db, Artwork
import os
import logging


# Set up logging
logging.basicConfig(level=logging.ERROR)  # Set to WARNING to reduce output, or ERROR to make it even less verbose

# Adjust logging level for SQLAlchemy specifically if needed
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_user_views.py


#set up the environmenta database

os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

#import the app
from app import app, CURR_USER_KEY

app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG'] = False
app.config['SQLALCHEMY_ECHO'] = False


class UserViewTestCase(TestCase):
    """Tests for user related routes"""
    @classmethod
    def setUp(cls):
        """Set up db before tests are run"""
        cls.client = app.test_client()
        cls.app_context = app.app_context()
        cls.app_context.push()
        db.create_all()  
        cls.populate_db()   

    @classmethod   
    def tearDown(cls):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    @classmethod 
    def populate_db(cls):
        """Set up the db with the initial data - helper method"""
        Century.query.delete()
        User.query.delete()
        Artwork.query.delete()
        
        c_18 = Century(century_name="18th Century")
        c_19 = Century(century_name="19th Century")
        c_20 = Century(century_name="20th Century")
        db.session.add_all([c_18, c_19, c_20])
        db.session.commit()

        cls.u1 = User.signup(username="testpotato",
                              first_name="Bob",
                              last_name="taco",
                              email="test@test.com",
                              password="testuser",
                              century_id=c_18.id)
        
        cls.u2 = User.signup(username="testuser2",
                              first_name="Bob2",
                              last_name="taco2",
                              email="test2@test.com",
                              password="testuser2",
                              century_id=c_19.id) 
        
        db.session.add_all([cls.u1, cls.u2])

        db.session.commit()

    def test_signup_route_get(self):
        """test the signup route -- get method"""
        with self.client as c:
            res = c.get('/signup')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('name="username"', html)
            self.assertIn('name="password"', html)
            self.assertIn('name="email"', html)
            self.assertIn('name="first_name"', html)
            self.assertIn('name="last_name"', html)
            self.assertIn('name="century_id"', html)
    
    def test_signup_route_post(self):
        """test the signup route -- post method"""
        with self.client as c:
            res = c.post('/signup', data={
                    'username': 'newuser',
                    'password': 'password',
                    'email': 'new@example.com',
                    'first_name': 'New',
                    'last_name': 'User',
                    'century_id': 1
                }, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<a class="navbar-form" href="/users/profile/edit">Edit Profile</a>', html)
            self.assertIn('New User', html)
            
    
    def test_login_get(self):
        """testing the login route -- get method"""
        with self.client as c:
            res = c.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('name="username"', html)
            self.assertIn('name="password"', html)
            self.assertIn('Welcome back!', html)

    def test_login_post(self):
        """"Testing the login route -- POST method."""
        with self.client as c:
            res = c.post('/login', data={
                'username': "testpotato", 
                'password': "testuser"
                }, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Bob taco', html)

    def test_logout(self):
        """tests the logout function of the application"""
        with self.client as c:
            res = c.get('/logout', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h2 class=\"join-message mb-4 display-3 text-center font-weight-bold\">Welcome back!</h2>", html)

    def test_user_profile_access_unauthorized(self):
        """Test accessing the user profile without being logged in"""
        with self.client as c:
            res = c.get('/users/profile', follow_redirects=True)
            html = res.get_data(as_text=True)
        
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_edit_profile(self):
        """Ensure the edit profile routes work"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            res = c.post('/users/profile', 
                            data={"username" : "HUMBOLDTSQUIDDEATH",
                                    "password" : "testuser",
                                    'century_id': 2}, follow_redirects=True)
            
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Bob taco', html)

    def test_user_profile_edit_unauthorized(self):
        """Testing the profile edit without being logged in"""
        with self.client as c:
            res = c.get('/users/profile', follow_redirects=True)
            html = res.get_data(as_text=True)
        
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_favorites_unauthorized(self):
        """Test the favorites route without a logged-in user."""
        with self.client as c:
            res = c.get('/users/favorites', follow_redirects=True)
            html = res.get_data(as_text=True)
        
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_favorites_empty(self):
        """Test the favorites route with a logged-in user."""
        with self.client as c:
            #simulate a login
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            
            res = c.get('/users/favorites')
            html = res.get_data(as_text=True)
        
            self.assertEqual(res.status_code, 200)
                #this should be empty and contain NO images
            self.assertIn("Favorites", html)
            self.assertNotIn("<img class=\"card-img-top img-fluid img-fixed-height\" src=\"{{ artwork.image_url }}\" alt=\"{{ artwork.title }}\"><div class=\"card-body\">", html)
