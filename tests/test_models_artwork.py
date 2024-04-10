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

class ArtworkModelTestCase(TestCase):
    """Tests for artwork model"""    """Tests for artwork related routes"""
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