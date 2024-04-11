#tests api_requests.py
#tests the code that talk to the API directory

#tests artwork.py
#tests the code that saves artwork to the db or to a file

import os

from unittest import TestCase
from unittest.mock import patch, MagicMock
from api_requests import APIRequests
from models import db, User, Century, Favorite, NotFavorite, Artwork, Artist
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
        User.query.delete()
        Century.query.delete()
        Artist.query.delete()
        Artwork.query.delete()
    
        #order of commiting is necessary
        century = Century(century_name='19th Century', id=1)
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


        test_art_s = Artwork(id=1, title="Yellow Octopus",artist_id=stacy.id, date_start=2020, date_end=2021, medium_display="coffee", image_id="yellowoctopus", image_url="www.testoctopus.jpg")
        test_art_a = Artwork(id=2, title="Cajun Red Panda", artist_id=allison.id, date_start=2020, date_end=2021, medium_display="crawfish", image_id="cajunredpanda", image_url="www.sample.jpg")
        db.session.add_all([test_art_a, test_art_s])
        db.session.commit()


        favorite = Favorite(id=1, user_id=user.id, artist_id=1, artwork_id=test_art_s.id)
        not_favorite = NotFavorite(id=2, user_id=user.id, artist_id=2, artwork_id=test_art_a.id)
        db.session.add_all([favorite, not_favorite])
        db.session.commit()

        self.user_id = user.id
        self.stacy = stacy
        self.allison = allison
        self.test_art_s = test_art_s
        self.test_art_a = test_art_a
        self.favorite = favorite
        self.not_favorite = not_favorite
        self.date_range = (2000, 2100)
        self.artwork = {self.test_art_a, self.test_art_s}
        


    # @patch('api_requests.requests.get')
    # def test_get_artworks(self, mock_get):
    #     """Test get_artworks with mocked API response"""
    #     mock_response = {
    #         "data": [
    #             # Mock data structure as expected from API
    #             {
    #                 "id": 1, 
    #                 "title": "Test Artwork", 
    #                 "artist_title": "Test Artist", 
    #                 'date_start': 1902,
    #                 'date_end': 2002,
    #                 'medium_display': "Watercolor",
    #                 'dimensions': "100x150",
    #                 'image_id': "second_test_image_id",
    #                 'image_url': "http://example.com/second_image.jpg"}
    #         ]
    #     }
    #     # Set up the mock_get response
    #     mock_get.return_value.json.return_value = mock_response
    #     mock_get.return_value.status_code = 200
      
    #     # Retrieve the user object from the database
    #     user = User.query.get(self.user_id)
        
    #     # Pass the user object to get_artworks
    #     res = APIRequests.get_artworks(user)
       
    #     # Assertions about the response
    #     self.assertEqual(len(res), len(mock_response['data']))
    #     for artwork_data, expected in zip(res, mock_response['data']):
    #         self.assertEqual(artwork_data.id, expected['id'])
    #         self.assertEqual(artwork_data.title, expected['title'])
            

    #     # Assert that the API was called with the correct URL and headers
    #     mock_get.assert_called_with(
    #         APIRequests.API_URL,
    #         headers=APIRequests.HEADER,
    #         params={'limit': 100, 'page': 1, 'fields': 'id,title,artist_title,image_id,dimensions,medium_display,date_display,date_start,date_end, artist_display'}
    #     )

    @patch('api_requests.Favorite.query')
    @patch('api_requests.NotFavorite.query')
    def test_filter(self, mock_not_fav_query, mock_fav_query):
        """Test the filtering of artworks based on favorites, not favorites, and date range."""
        # Mock the favorite and not favorite artwork IDs
        mock_fav_query.filter_by.return_value.all.return_value = [MagicMock(spec=Favorite, artwork_id=1)]
        mock_not_fav_query.filter_by.return_value.all.return_value = [MagicMock(spec=NotFavorite, artwork_id=2)]
         # Call the filter_artworks class method
        filtered_artworks = APIRequests.filter_artworks(
            self.artwork, 
            self.favorite, 
            self.not_favorite, 
            self.date_range
        )

        # Assertions to verify the correct filtering of artworks
        self.assertEqual(len(filtered_artworks), 1)  # Only one artwork should match the criteria
        self.assertEqual(filtered_artworks[0]['id'], 1)  # Verify the ID of the artwork returned
