
#tests api_requests.py
#tests the code that talk to the API directory

#tests artwork.py
#tests the code that saves artwork to the db or to a file

import os

from unittest import TestCase
from unittest.mock import patch, MagicMock, call
from api_requests import APIRequests
from models import db, User, Century, Favorite, NotFavorite, Artwork, Artist
from app import app, CURR_USER_KEY
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Set to WARNING to reduce output, or ERROR to make it even less verbose

# Adjust logging level for SQLAlchemy specifically if needed
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

app.config['WTF_CSRF_ENABLED'] = False
os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"


# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_api_requests.py

class TestAPIRequests(TestCase):
    """Tests the APIRequests Class and its properties"""
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
        """Runs before each test"""
        Favorite.query.delete()
        NotFavorite.query.delete()
        User.query.delete()
        Century.query.delete()
        Artist.query.delete()
        Artwork.query.delete()
    
        #order of commiting is necessary
        century = Century(id=1, century_name='19th Century')
        db.session.add(century)
        db.session.commit()
        #user references century, so commit century prior to user
        user = User(
            id=1,
            username='testuser',
            password='testpassword',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            century_id=1
        )
        db.session.add(user)
        db.session.commit()

        stacy = Artist(id=1, artist_title='Stacy Smith', artist_display="Yellow Octopus")
        allison = Artist(id=2, artist_title='Allison Currie', artist_display="Cajun Red Panda")
        db.session.add_all([stacy, allison])
        db.session.commit()


        test_art_s = Artwork(id=1, title="Yellow Octopus",artist_id=stacy.id, date_start=1820, date_end=1821, medium_display="coffee", image_id="yellowoctopus", image_url="www.testoctopus.jpg")
        test_art_a = Artwork(id=2, title="Cajun Red Panda", artist_id=allison.id, date_start=1820, date_end=1821, medium_display="crawfish", image_id="cajunredpanda", image_url="www.sample.jpg")
        test_art_f = Artwork(id=3, title="Cajun Red Panda Duex", artist_id=allison.id, date_start=1820, date_end=1821, medium_display="crawfish and mardi gras beads", image_id="cajunredpandaz", image_url="www.sample.jpg")
        db.session.add_all([test_art_a, test_art_s, test_art_f])
        db.session.commit()

        favorite = Favorite(id=1, user_id=user.id, artist_id=1, artwork_id=test_art_s.id)
        not_favorite = NotFavorite(id=2, user_id=user.id, artist_id=2, artwork_id=test_art_a.id)
        db.session.add_all([favorite, not_favorite])
        db.session.commit()

        self.mock_api_response = {
            'data': [{
            'id': 4,
            'title': "The Great taco cat",
            'artist_title': "Neri Gomez-Brahm",
            'image_id': "mi sobrino es guapo",
            'dimensions': '100x100',
            'medium_display': 'guacomole',
            'date_display': '1880',
            'date_start': 1880,
            'date_end': 1885,
            'artist_display': "Neri is the best",
            'image_url': f'http://tacooooos.jpg'
        }for i in range(50)]
        }
        
        self.test_art_s = test_art_s
        self.test_art_a = test_art_a
        self.test_art_f = test_art_f
        self.date_range = ("1800" , "1899")
        self.user = user
        self.favorite = favorite
        self.not_favorite = not_favorite
        self.century = century

    @patch('api_requests.requests.get')
    def test_get_artworks(self, mock_get):
        """Test get_artworks with mocked API response"""
        mock_response  = {
            "data": [
                {
                    "id": 1, 
                    "title": "Yellow Octopus", 
                    "artist_title": "Stacy Smith", 
                    'date_start': 1820,
                    'date_end': 1821,
                    'medium_display': "coffee",
                    'dimensions': "100x150",
                    'image_id': "yellowoctopus",
                    'image_url': "http://example.com/yellowoctopus.jpg"
                } for i in range(10) #Making math easy -- each call recievees 10 items
            ] 
        }
        # Set up the mock_get response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
    
        # simulate getting all needed artowrks within 5 API calls
        artworks, error = APIRequests.get_artworks(self.user)
        
        
        self.assertEqual(len(artworks), 50) #equally the amount wanted
        self.assertIsNone(error)
        self.assertTrue(mock_get.call_count <= 6) #ensure not too many calls are sent
        self.assertEqual(artworks[0].title, "Yellow Octopus")
        self.assertEqual(artworks[0].artist.artist_title, "Stacy Smith")
        
    @patch('api_requests.requests.get')
    @patch('api_requests.Favorite.query')
    @patch('api_requests.NotFavorite.query')
    @patch('api_requests.Century.query')
    def test_get_artworks_call(self, mock_century_query, mock_not_fav_query, mock_fav_query, mock_get):
        # Mock the database queries
        mock_century_query.get.return_value = self.century
        mock_fav_query.filter_by.return_value.all.return_value = [self.favorite]
        mock_not_fav_query.filter_by.return_value.all.return_value = [self.not_favorite]

        # Mock the requests.get call
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = self.mock_api_response
        mock_get.return_value = mock_get_response

        # Wrap the function call inside a test request context
        with self.client.application.test_request_context('/users/profile'):
            result = APIRequests.get_artworks(self.user)


        # Assertions to check if function behaved as expected
        self.assertEqual(len(result), 2)

    @patch('api_requests.requests.get')
    def test_get_artworks_empty_response(self, mock_get):
        """Test get_artworks when the API returns an empty list of artworks."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': []}
        mock_get.return_value = mock_response

        # Execute the function under test
        artworks, error = APIRequests.get_artworks(self.user)

        # Assert that the artworks list is empty
        self.assertEqual(len(artworks), 0)
        # Assert that there is no error
        self.assertIsNone(error)
        # Assert that the get request was called correctly
        mock_get.assert_called_once()

    @patch('api_requests.requests.get')
    @patch('flask.flash')
    def test_get_artworks_api_failure(self, mock_flash, mock_get):
        """Test handling of non-200 response from the API."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_get.return_value = mock_response

        with app.test_request_context():
            #above method This method creates an explicit request context which mimics an HTTP request.\
            # It can be more reliable when you want to control the context more directly than what with self.client: provides.
            artworks, error = APIRequests.get_artworks(self.user)

        # Assertions to ensure the behavior is as expected
        self.assertIn(error, 'Failed with status code 500')
        self.assertListEqual(artworks, [])
