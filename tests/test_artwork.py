#tests artwork.py
#tests the code that saves artwork to the db or to a file

import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from models import db, Artwork, Artist
from artwork import SaveArtwork
from app import app, CURR_USER_KEY
from flask import current_app, get_flashed_messages
import logging


# Set up logging
logging.basicConfig(level=logging.ERROR)  # Set to WARNING to reduce output, or ERROR to make it even less verbose

# Adjust logging level for SQLAlchemy specifically if needed
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
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
        id=1  
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
        with patch('artwork.requests.get') as mock_get:
            mock_get.start()
            #configure the mock to return a response with a succesful status code & binary
            mock_get.return_value.status_code = 200
            

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

            # self.assertTrue(mock_flash.called)
            self.assertTrue(mock_get.called)

            # Build the file path
            test_image_path = os.path.join(TEST_IMAGES_DIR, f"{title.replace(' ', '_')}_{image_id}.jpg")

            
            #assert taht the file was created
            self.assertTrue(os.path.exists(TEST_IMAGES_DIR))

            if os.path.exists(test_image_path):
                os.remove(test_image_path)

           
    @patch('artwork.flash')
    def test_save_artwork_flash_on_error(self, mock_flash):
        """Test that a flash message is sent on database error."""
        artwork_detail = {
            'id': 13,
            'title': "Color Theory",
            'artist_title': "Taylor swift",
            'date_start': 1989,
            'date_end': 2079,
            'medium_display': "Oil on Canvas",
            'dimensions': "200x300",
            'image_id': "cats",
            'image_url': "http://cats.com/image.jpg"
        }

        with patch('artwork.db.session.commit', side_effect=Exception("DB Error")):
            result = SaveArtwork.save_artwork(artwork_detail)
            self.assertIsNone(result)
            mock_flash.assert_called_with('An error occurred while saving the artist: DB Error', 'danger')

    @patch('artwork.requests.get')
    @patch('artwork.flash')
    def test_save_image_file_flash_success(self, mock_flash, mock_get):
        """Ensure flash message is triggered correctly on successful image download."""
        # Set up the mock return value
        mock_get.return_value.status_code = 200
            #using the b'' represents the byte string used in responses from servers\
            #this simulates teh behavior of a successful HTTP GET reuest that retrieves
            #data from a specified URL w/o performing the network operation
        mock_get.return_value.content = b'fake-image-content'

        image_id = "1adf2696-8489-499b-cad2-821d7fde4b33"
        image_url = "https://www.artic.edu/iiif/2/2d484387-2509-5e8e-2c43-22f9981972eb/full/843,/0/default.jpg"
        title = "A Sunday on La Grande Jatte — 1884"

        # Expected path where the image should be saved
        expected_image_path = os.path.join(current_app.static_folder, 'images', f"{title.replace(' ', '_')}_{image_id}.jpg")

        # Call the method under test
        SaveArtwork.save_image_file(image_url, image_id, title)

        # Check if the file exists and clean up
        self.assertTrue(os.path.exists(expected_image_path))
        os.remove(expected_image_path)

        # Ensure flash was called with success message
        mock_flash.assert_called_with("Images successfully saved.", "success")
