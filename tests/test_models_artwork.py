#tests model.py
#tests the User Model

from unittest import TestCase
from models import User, Artist, Artwork, Favorite, Century, Classification, db
import os
import logging


# Set up logging
logging.basicConfig(level=logging.WARNING)  # Set to WARNING to reduce output, or ERROR to make it even less verbose

# Adjust logging level for SQLAlchemy specifically if needed
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_models_artwork.py


#set up the environmenta database

os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

#import the app
from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

class ArtworkModelTestCase(TestCase):
    """Tests for artwork model"""   
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
        """Clean up existing data and provide a fresh database before each test.""" 
        Artwork.query.delete()
        Artist.query.delete()
        # Create a sample artist for associating with artworks
        self.artist = Artist(artist_title="Test Artist", artist_display="Sample biography")
        db.session.add(self.artist)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()

    def test_artwork_creation(self):
        """Test creating an artwork and verifying its properties."""
        new_artwork = Artwork(title="Test Artwork", artist_id=self.artist.id, image_url="http://example.com/art.jpg")
        db.session.add(new_artwork)
        db.session.commit()

        # Verify artwork was created and associated correctly
        artwork = Artwork.query.first()
        self.assertIsNotNone(artwork)
        self.assertEqual(artwork.title, "Test Artwork")
        self.assertEqual(artwork.artist_id, self.artist.id)
        self.assertEqual(artwork.image_url, "http://example.com/art.jpg")
        # Verify artist association
        self.assertEqual(artwork.artist.artist_title, self.artist.artist_title)
