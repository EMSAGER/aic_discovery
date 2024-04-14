
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
        test_art_f = Artwork(id=3, title="Cajun Red Panda Duex", artist_id=allison.id, date_start=2020, date_end=2021, medium_display="crawfish and mardi gras beads", image_id="cajunredpandaz", image_url="www.sample.jpg")
        db.session.add_all([test_art_a, test_art_s, test_art_f])
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
        self.test_art_f = test_art_f
        self.favorite = favorite
        self.not_favorite = not_favorite
        self.date_range = (2000, 2100)
        
    # @patch('api_requests.requests.get')
    # def test_get_artworks(self, mock_get):
    #     """Test get_artworks with mocked API response"""
    #     mock_response = {
    #         "data": [
    #             {
    #                 "id": 1, 
    #                 "title": "Test Artwork", 
    #                 "artist_title": "Test Artist", 
    #                 'date_start': 1902,
    #                 'date_end': 2002,
    #                 'medium_display': "Watercolor",
    #                 'dimensions': "100x150",
    #                 'image_id': "second_test_image_id",
    #                 'image_url': "http://example.com/second_image.jpg"
    #             }
    #         ]
    #     }
    #     # Set up the mock_get response
    #     mock_get.return_value.json.return_value = mock_response
    #     mock_get.return_value.status_code = 200
    
    #     # Retrieve the user object from the database
    #     user = User.query.get(self.user_id)
        
    #     # Create an instance of APIRequests
    #     api_requests = APIRequests()

    #     # Pass the user object to get_artworks on the instance
    #     res = api_requests.get_artworks(user)
    
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

        # Create a list of artwork instances for the test
        artworks = [self.test_art_s, self.test_art_a, self.test_art_f]

        # Lists of IDs to simulate what should be returned from actual database queries
        favorite_ids = [fav.artwork_id for fav in mock_fav_query.filter_by.return_value.all()]
        not_favorite_ids = [not_fav.artwork_id for not_fav in mock_not_fav_query.filter_by.return_value.all()]

         # Call the filter_artworks class method
        filtered_artworks = APIRequests.filter_artworks(
            artworks, 
            favorite_ids, 
            not_favorite_ids, 
            self.date_range
        )

        # Assertions to verify the correct filtering of artworks
        self.assertEqual(len(filtered_artworks), 1)  # Only one artwork should match the criteria
        self.assertEqual(filtered_artworks[0]['id'], self.test_art_f.id)
        self.assertEqual(favorite_ids, [1]) #test the favorite.artwork.id is correct
        self.assertEqual(not_favorite_ids, [2]) #test the not_favorite.artwork.id
