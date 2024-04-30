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
        self.populate_db()
        
       
    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    
    def populate_db(self):
        """Add sample data to the database."""
        db.drop_all()
        db.create_all()
        
        artist = Artist(artist_title="Vincent van Gogh", artist_display="Dutch post-impressionist painter")
        db.session.add(artist)
        db.session.commit()

        artwork = Artwork(
            title="Starry Night",
            artist_id=artist.id,
            date_start=1889,
            date_end=1889,
            medium_display="Oil on canvas",
            dimensions="73.7 cm × 92.1 cm",
            image_url="http://wwww.example.starry_night.jpg"
        )
        db.session.add(artwork)
        db.session.commit()

        self.artist_id = artist.id
        self.artwork_id = artwork.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()

    def test_artwork_creation(self):
        """Test creating an artwork and verifying its properties."""
        artwork = Artwork.query.get(self.artwork_id)
        self.assertIsNotNone(artwork)
        self.assertEqual(artwork.title, "Starry Night")
        self.assertEqual(artwork.artist_id, self.artist_id)
        self.assertEqual(artwork.medium_display, "Oil on canvas")

    def test_artwork_update(self):
        """Test updating an artwork's properties."""
        artwork = Artwork.query.get(self.artwork_id)
        artwork.title = "The Starry Night"
        db.session.commit()

        updated_artwork = Artwork.query.get(self.artwork_id)
        self.assertEqual(updated_artwork.title, "The Starry Night")

    def test_artwork_deletion(self):
        """Test deleting an artwork."""
        artwork = Artwork.query.get(self.artwork_id)
        db.session.delete(artwork)
        db.session.commit()

        deleted_artwork = Artwork.query.get(self.artwork_id)
        self.assertIsNone(deleted_artwork)

    def test_artist_relationship(self):
        """Test the relationship between Artwork and Artist."""
        artwork = Artwork.query.get(self.artwork_id)
        self.assertEqual(artwork.artist.artist_title, "Vincent van Gogh")