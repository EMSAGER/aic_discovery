#tests artwork.py
#tests the code that saves artwork to the db or to a file

import os
from unittest import TestCase
from models import db, Artwork, Artist
from artwork import SaveArtwork
from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_artwork.py

class TestSaveArtwork(TestCase):
    """Tests the Save Artwork Class and its properties"""
    def setUp(self):
        """Create test client add sample data"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()  
        db.create_all()

    def tearDown(self):
        """Tear down test application context and drop all tables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_save_artwork_creates_new(self):
        """Test saving a new artowrk correctly updates the database"""
        artist_title = "Test Artist"
        artwork_detail = {
            'id': 1,
            'title': "Test Artwork",
            'artist_title': artist_title,
            'date_start': 1900,
            'date_end': 2000,
            'medium_display': "Oil on Canvas",
            'dimensions': "200x300",
            'image_id': "test_image_id",
            'image_url': "http://example.com/image.jpg"
        }

        res = SaveArtwork.save_artwork(artwork_detail)

        self.assertIsNotNone(res)
        self.assertEqual(Artwork.query.count(),1)
        self.assertEqual(Artist.query.count(), 1)
        self.assertEqual(Artwork.query.first().title, artwork_detail['title'])
        self.assertEqual(Artist.query.first().artist_title, artist_title)

    def test_update_existing_artwork(self):
        """Test updating an existing artwork."""
        # First, create an artwork
        self.test_save_artwork_creates_new()
        # Then, update the artwork with new details
        artwork_update = {
            'id': 1,  # Same ID as in `test_save_artwork_creates_new`
            'title': "Updated Test Artwork",
            'artist_title': "Test Artist",
            'date_start': 1901,
            'date_end': 2001,
            'medium_display': "Updated Medium",
            'dimensions': "200x301",
            'image_id': "updated_test_image_id",
            'image_url': "http://example.com/updated_image.jpg"
        }
        SaveArtwork.save_artwork(artwork_update)
        updated_artwork = Artwork.query.get(1)
        self.assertEqual(updated_artwork.title, "Updated Test Artwork")

    def test_save_artwork_with_existing_artist(self):
        """Test saving an artwork with an existing artist."""
        # Ensure an artist exists
        self.test_save_artwork_creates_new()
        # Create new artwork with the same artist
        new_artwork_detail = {
            'id': 2,
            'title': "Second Test Artwork",
            'artist_title': "Test Artist",  # Same artist
            'date_start': 1902,
            'date_end': 2002,
            'medium_display': "Watercolor",
            'dimensions': "100x150",
            'image_id': "second_test_image_id",
            'image_url': "http://example.com/second_image.jpg"
        }

        SaveArtwork.save_artwork(new_artwork_detail)
        
        self.assertEqual(Artwork.query.count(), 2)
        self.assertEqual(Artist.query.count(), 1)

    def test_save_image_file(self):
        """Testing downloading and image from the image_url and saving it the static file"""