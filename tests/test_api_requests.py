#tests api_requests.py
#tests the code that talk to the API directory

#tests artwork.py
#tests the code that saves artwork to the db or to a file

import os
import shutil
from unittest import TestCase
from unittest.mock import patch
from models import db, Artwork, Artist
from artwork import SaveArtwork
from app import app, CURR_USER_KEY
from flask import current_app

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
        #create a sample
        artist = Artist(artist_title="Test Artist")
        db.session.add(artist)
        db.session.commit()

        artwork = Artwork(
        title="Seed Art",
        artist_id=artist.id,
        image_url="https://example.com/image.jpg",
        id=1  # Make sure to add an ID here if your model doesn't auto-generate it
    )
        db.session.add(artwork)
        db.session.commit()

        self.artist = artist
        self.artwork = artwork

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
            'id': 1,
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
        #mock the `requests.get` method & return a mock response with status code 200 & mock the flash
        with patch('artwork.requests.get') as mock_get, patch('artwork.flash') as mock_flash:
            #configure the mock to return a response with a succesful status code & binary
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b'test_image_content'

            #title & image_id to use for testing
            title = self.artwork.title
            image_id = self.artwork.image_id
            image_url = self.artwork.image_url

            # Ensure the test_images subfolder exists within the static folder
            TEST_IMAGES_SUBFOLDER = 'test_images'
            TEST_IMAGES_DIR = os.path.join(current_app.static_folder, TEST_IMAGES_SUBFOLDER)
            os.makedirs(TEST_IMAGES_DIR, exist_ok=True) 

            # Call the save_image_file method
            SaveArtwork.save_image_file(image_url, image_id, title)

            # Build the file path
            test_image_path = os.path.join(TEST_IMAGES_DIR, f"{title.replace(' ', '_')}_{image_id}.jpg")

            
            #assert taht the file was created
            self.assertTrue(os.path.exists(TEST_IMAGES_DIR))

            if os.path.exists(test_image_path):
                os.remove(test_image_path)

            #assert the flash occurred
            mock_flash.assert_called_with("Images successfully saved.", "success")