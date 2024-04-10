#tests api_requests.py
#tests the code that talk to the API directory

#tests artwork.py
#tests the code that saves artwork to the db or to a file

import os

from unittest import TestCase
from unittest.mock import patch, MagicMock
from api_requests import APIRequests
from models import db, User, Century, Favorite, NotFavorite
from app import app, CURR_USER_KEY
from flask import current_app

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

        user = User(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            century_id=1
        )
        century = Century(century_name='19th Century', id=1)
        db.session.add_all([user, century])
        db.session.commit()

        self.user_id = user.id


    @patch('api_requests.requests.get')
    def test_get_artworks(self, mock_get):
        """Test get_artworks with mocked API response"""
        mock_response = {
            "data": [
                # Mock data structure as expected from API
                {
                    "id": 1, 
                    "title": "Test Artwork", 
                    "artist_title": "Test Artist", 
                    'date_start': 1902,
                    'date_end': 2002,
                    'medium_display': "Watercolor",
                    'dimensions': "100x150",
                    'image_id': "second_test_image_id",
                    'image_url': "http://example.com/second_image.jpg"}
            ]
        }
        # Set up the mock_get response
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200
      
        # Retrieve the user object from the database
        user = User.query.get(self.user_id)
        
        # Pass the user object to get_artworks
        res = APIRequests.get_artworks(user)
       
        # Assertions about the response
        self.assertEqual(len(res), len(mock_response['data']))
        for artwork_data, expected in zip(res, mock_response['data']):
            self.assertEqual(artwork_data.id, expected['id'])
            self.assertEqual(artwork_data.title, expected['title'])
            

        # Assert that the API was called with the correct URL and headers
        mock_get.assert_called_with(
            APIRequests.API_URL,
            headers=APIRequests.HEADER,
            params={'limit': 100, 'page': 1, 'fields': 'id,title,artist_title,image_id,dimensions,medium_display,date_display,date_start,date_end, artist_display'}
        )