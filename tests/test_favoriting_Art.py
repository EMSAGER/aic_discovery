from unittest import TestCase
from models import User, Century, db, Artwork, Artist, Favorite, NotFavorite
import os
import logging


# Set up logging
logging.basicConfig(level=logging.WARNING)  # Set to WARNING to reduce output, or ERROR to make it even less verbose

# Adjust logging level for SQLAlchemy specifically if needed
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_favoriting_Art.py


#set up the environmenta database

os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

#import the app
from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

class ArtworkViewTestCase(TestCase):
    """Tests for artwork related routes"""
    def setUp(self):
        """Create test client add sample data"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()  
        db.create_all()
        self.populate_db()
        
       
    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def populate_db(self):
        """Set up the db with the initial data - helper method"""
        User.query.delete()
        Century.query.delete()
        Artwork.query.delete()
        Favorite.query.delete()
        
        c_18 = Century(century_name="18th Century")
        db.session.add(c_18)
        db.session.commit()

        Stacy = Artist(artist_title="Stacy Smith", artist_display="TAAACOS")
        Allison = Artist(artist_title="Allison Currie", artist_display="CRAWFISH")
        db.session.add_all([Stacy, Allison])
        db.session.commit()

        self.test_art_s = Artwork(title="Does Allison love Em more than queso?",
                                  artist_id=Stacy.id, 
                                  image_url="https://example.com/art_s.jpg")
        self.test_art_a = Artwork(title="Does Stacy love Em more than yellow octopus?",
                                  artist_id=Allison.id, 
                                  image_url="https://example.com/art_a.jpg")

        db.session.add_all([self.test_art_s, self.test_art_a])
        db.session.commit()

        self.u1 = User.signup(username="testpotato",
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

    def test_favorites_add(self):
       """Test adding an artwork to favorites."""
       with self.client as c:
                #simulate a login
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id

                
                res = c.post('/users/profile', data={'artwork_id': self.test_art_s.id, 'action': 'favorite'}, follow_redirects=True)
                html = res.get_data(as_text=True)
            
                self.assertEqual(res.status_code, 200)
                self.assertIn("18th Century", html)

                favorite = Favorite.query.filter_by(user_id=self.u1.id, artwork_id=self.test_art_s.id).first()
                self.assertIsNotNone(favorite)

    def test_unfavorites_add(self):
       """Test adding an artwork to favorites."""
       with self.client as c:
                #simulate a login
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.u1.id

                
                res = c.post('/users/profile', data={'artwork_id': self.test_art_a.id, 'action': 'not_favorite'}, follow_redirects=True)
                html = res.get_data(as_text=True)
            
                self.assertEqual(res.status_code, 200)
                self.assertIn("18th Century", html)

                not_favorite = NotFavorite.query.filter_by(user_id=self.u1.id, artwork_id=self.test_art_s.id).first()
                self.assertIsNone(not_favorite)