from unittest import TestCase
from unittest.mock import patch
from models import User, Century, db, Artwork, Artist, Favorite, NotFavorite
import os
import logging
from flask_sqlalchemy import SQLAlchemy

# Set up logging
logging.basicConfig(level=logging.ERROR)  # Set to WARNING to reduce output, or ERROR to make it even less verbose

# Adjust logging level for SQLAlchemy specifically if needed
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

# run these tests like:
#
#    FLASK_ENV=production python3 -m coverage run -m unittest tests/test_surprise.py


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
        db.session.commit()
        self.app_context.pop()

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
    def test_surprise_me_favorite(self, mock_surprise_me):
        """Test POST action for favoriting an artwork via the Surprise me route"""
        #setup mock
       
        mock_artwork = [
            {'title': 'Mona Lisa', 'image_url': 'http://example.com/mona.jpg', 'artist_id': 1, 'artwork_id': 1}
        ]
        mock_surprise_me.return_value = (mock_artwork, '20th Century')

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

                new_artist = Artist(id=1, artist_title='Leonardo da Vinci')
                db.session.add(new_artist)
                new_artwork = Artwork(id=1, title='Mona Lisa', artist_id=new_artist.id, image_url='http://example.com/mona.jpg')
                db.session.add(new_artwork)
                db.session.commit()
            # Sending POST request to the route
                res = c.post('/users/surprise', data={'action': 'favorite', 'artwork_id': 1}, follow_redirects=True)
                html = res.get_data(as_text=True)

                self.assertEqual(res.status_code, 200)
                
                # Fetch the favorite from the database
                f = Favorite.query.filter_by(artwork_id = 1)
                
                #check db to see if favorite is added
                self.assertIsNotNone(f)
                self.assertIn("Mona Lisa", html)
                
    @patch('app.APIRequests.surprise_me')
    def test_surprise_me_not_favorite(self, mock_surprise_me):
        """Test POST action for un-favoriting/disliking an artwork via the suprise me route"""
        #setup mock
        mock_dislike = [
            {'title': 'Water Lillies', 'image_url': 'http://example.com/lillies.jpg', 'artist_id': 2, 'artwork_id': 2}
        ]
        mock_surprise_me.return_value = (mock_dislike, '20th Century')

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

                new_dis_artist = Artist(id=2, artist_title='Claude Monet')
                db.session.add(new_dis_artist)
                new_dislike = Artwork(id=2, title='Water Lillies', artist_id= new_dis_artist.id, image_url='http://example.com/lillies.jpg')
                db.session.add(new_dislike)
                db.session.commit()

                #send POST request including new action
                res = c.post('/users/surprise', data={'action': 'not_favorite', 'artwork_id': 2}, follow_redirects=True)
                
                self.assertEqual(res.status_code, 200)

                nf = NotFavorite.query.filter_by(artwork_id=2)
                self.assertIsNotNone(nf)