#tests the relationships between models


import os
from unittest import TestCase
from models import db, Artwork, Artist, Favorite, NotFavorite, User, Artist, Artwork, Favorite, NotFavorite, Century
from app import app, CURR_USER_KEY
import logging

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_models_relationships.py


#set up the environmenta database


# Set up logging
logging.basicConfig(level=logging.ERROR)  # Set to WARNING to reduce output, or ERROR to make it even less verbose

# Adjust logging level for SQLAlchemy specifically if needed
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
app.config['WTF_CSRF_ENABLED'] = False
os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"


class ModelsRelationshipTestCase(TestCase):
    """Tests relationships between models."""
    
    def setUp(self):
        """Create test client add sample data"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()  
        self.populate_db()

    def populate_db(self):
        """Add sample data to the database."""
        db.drop_all()
        db.create_all()
        
        century = Century(century_name="19th Century")
        db.session.add(century)
        db.session.commit()

        user = User(username="testuser", password="testpassword", email="test@example.com", first_name="Test", last_name="User", century_id=1)
        artist = Artist(artist_title="Claude Monet", artist_display="French painter, founder of Impressionist movement.")
        db.session.add_all([user, artist])
        
        artwork_f = Artwork(id=6, title="Water Lilies", artist=artist, date_start=1916, date_end=1919, medium_display="Oil on canvas", image_url="http://example.com/water_lilies.jpg")
        artwork_nf = Artwork(id=7, title="Hay Stacks", artist=artist, date_start=1916, date_end=1919, medium_display="Oil on canvas", image_url="http://example.com/hay_stacks.jpg")
        db.session.add_all([artwork_f, artwork_nf])

        db.session.commit()

        # Adding favorites and not favorites
        favorite = Favorite(user_id=user.id, artist_id=artist.id, artwork_id=artwork_f.id)
        not_favorite = NotFavorite(user_id=user.id, artist_id=artist.id, artwork_id=artwork_nf.id)
        db.session.add_all([favorite, not_favorite])
        db.session.commit()

        self.user = user
        self.century = century
        self.artist = artist
        self.artwork_f = artwork_f
        self.artwork_nf = artwork_nf
        self.favorite = favorite
        self.not_favorite = not_favorite

    def tearDown(self):
        """Clean up any fouled transactions."""
        db.session.remove()
        db.drop_all()
        
    def test_favorite_relationships(self):
        """Testing that the favorite relationships are set up correctly."""
        f = Favorite.query.first()
        # Access user object directly via relationships.
        self.assertEqual(f.user.id, self.user.id)
        # Access artwork object and its properties directly via relationships.
        self.assertEqual(f.artwork_id, self.artwork_f.id)
        self.assertEqual(f.artist_id, self.artist.id)
        # Confirming that the correct artwork and artist details are fetched
        self.assertEqual(f.artwork.title, "Water Lilies")
        self.assertEqual(f.artist.artist_title, "Claude Monet")
    
    def test_not_favorite_relationships(self):
        """Test the relationship of the NotFavorite model."""
        nf = NotFavorite.query.first()
        # Access user object directly via relationships.
        self.assertEqual(nf.user.id, self.user.id)
         # Access artwork object and its properties directly via relationships.
        self.assertEqual(nf.artwork_id, self.artwork_nf.id)
        self.assertEqual(nf.artist_id, self.artist.id)
        # Confirming that the correct artwork and artist details are fetched
        self.assertEqual(nf.artwork.title, "Hay Stacks")
        self.assertEqual(nf.artist.artist_title, "Claude Monet")

    def test_artist_creation(self):
        """Test artist creation and properties."""
        artist = Artist.query.first()
        self.assertEqual(artist.artist_title, "Claude Monet")
        self.assertEqual(artist.artist_display, "French painter, founder of Impressionist movement.")

    def test_century_creation(self):
        """Test century creation and properties."""
        century = Century.query.first()
        self.assertEqual(century.century_name, "19th Century")


        