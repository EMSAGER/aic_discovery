from unittest import TestCase
from unittest.mock import patch
import api_requests
from models import User, Century, db, Artwork, Artist, Favorite, NotFavorite
import os
import logging


# Set up logging
logging.basicConfig(level=logging.ERROR)  # Set to WARNING to reduce output, or ERROR to make it even less verbose

# Adjust logging level for SQLAlchemy specifically if needed
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_surprise.py


#set up the environmenta database

os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

#import the app
from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

class SurpriseViewTestCase(TestCase):
    """Tests for the surprise related routes"""
    def setUp(self):
        """Create test client add sample data"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()  
        self.populate_db()
        
       
    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def populate_db(self):
        """Set up the db with the initial data - helper method"""
        db.drop_all()
        db.create_all()
        
        c_18 = Century(century_name="18th Century")
        db.session.add(c_18)
        db.session.commit()

        self.u1 = User.signup(
                              username="testpotato",
                              first_name="Bob",
                              last_name="taco",
                              email="test@test.com",
                              password="testuser",
                              century_id=c_18.id)
        
        db.session.add(self.u1)
        db.session.commit()
        
    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()

    def test_surprise_me_unauthorized(self):
        """Test accessing Surprise Me route without logging in."""
        with self.client as c:
            res = c.get('/users/surprise', follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    @patch('app.APIRequests.surprise_me')
    def test_suprise_me(self, mock_surprise_me):
        """Test accessing Surprise Me route with a logged-in user."""
        # Setup mock
        mock_surprise_me.return_value = ([{'title': 'Mona Lisa', 'image_url': 'http://example.com/mona.jpg'}], '18th Century')

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            res = c.get('/users/surprise')
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Mona Lisa", html)

    @patch('app.APIRequests.surprise_me')
    def test_surprise_me_favorite_(self, mock_surprise_me):
        """Test POST action for favoriting an artwork via the Surprise me route"""
        #setup mock
        mock_artwork = [
            {'title': 'Mona Lisa', 'image_url': 'http://example.com/mona.jpg', 'artist_id': 1, 'artwork_id': 1}
        ]
        mock_surprise_me.return_value = (mock_artwork, '20th Century')

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            # Sending POST request to the route
                res = c.post('/users/surprise', data={'action': 'favorite', 'user_id': self.u1.id, 'artwork_id': 1,}, follow_redirects=True)

                self.assertEqual(res.status_code, 200)

                # Fetch the favorite from the database
                f = Favorite.query.first()
                
                #check db to see if favorite is added
                self.assertIsNotNone(f)
                self.assertEqual(f.user_id, self.u1.id)
                self.assertEqual(f.artwork_id, 1)

