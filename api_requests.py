#user -- century
#favorite & not favorite artowrk
###this should handle the response requests

#originally the get_artworks method was a multi-step method. I keep having issues with 
#testing, I'm now breaking it up. 
#changed the filtering from client side to API side
import requests
import random
from flask import flash
from models import Favorite, NotFavorite, Century
from artwork import SaveArtwork

save_artwork = SaveArtwork.save_artwork


class APIRequests:
    CURR_USER_KEY = "curr_user"
    API_URL = "https://api.artic.edu/api/v1/artworks/search"
    HEADER = {
        'AIC-User-Agent': 'AIC Discovery (emsager7@gmail.com)'
    }
    century_dates ={
        '18th Century': ('1700', '1799'),
        '19th Century': ('1800', '1899'),
        '20th Century': ('1900', '1999'),
    }

    @classmethod
    def filter_dates(cls, artwork, user_century):
        """Utility method for filtering artwork"""
        date_range = cls.century_dates.get(user_century, (None, None))
        if date_range == (None, None):
            return None
        
        date_start = int(artwork['date_start'])
        date_end = int(artwork['date_end'])
        date_range_start, date_range_end = map(int, date_range)
        
        if date_range_start <= date_start <= date_range_end or date_range_start <= date_end <= date_range_end:
            return artwork
        else:
            return None
    
   
    @classmethod
    def fetch_artworks_from_api(cls, query_params):
        """Fetch artwork data from the API"""
        try:
            response = requests.get(cls.API_URL, headers=cls.HEADER, params=query_params)
            if response.status_code == 200:
                return response.json()['data'], None
            else:
            # Properly handle non-200 responses
                flash(f"Failed to fetch artworks from API: {response.status_code}", "danger")
                return None, f"Failed with status code {response.status_code}"
        except requests.RequestException as e:
            # Handle connection errors
            flash(f"Error connecting to the Art Institute of Chicago API: {e}", "danger") 
            return None, str(e)
        
    @classmethod
    def fetch_favorite_and_not_favorite_ids(cls, user_id):
        """Utility method to fetch favorite and not favorite IDs"""
        favorite_artwork_ids = [fav.artwork_id for fav in Favorite.query.filter_by(user_id=user_id).all()]
        not_favorite_artwork_ids = [not_fav.artwork_id for not_fav in NotFavorite.query.filter_by(user_id=user_id).all()]
        return favorite_artwork_ids, not_favorite_artwork_ids
    
    @classmethod
    def get_artworks(cls, user):
        """Method to get artwork from the API"""
        user_century = Century.query.get(user.century_id).century_name
        
        total_art_for_app = 50
        saved_artworks = []
        page = 1

        favorite_artwork_ids, not_favorite_artwork_ids = cls.fetch_favorite_and_not_favorite_ids(user.id)

        #define API parameters with filtering
        query_params = {
            'limit': 100,
            'page' : page,
            'fields': 'id,title,artist_title,image_id,dimensions,medium_display,date_display,date_start,date_end, artist_display',
            'excluded_ids': ','.join(map(str, favorite_artwork_ids + not_favorite_artwork_ids))
        }

        #fetch data until enough artworks are collected
        while len(saved_artworks) < total_art_for_app:
            artworks_details, error = cls.fetch_artworks_from_api(query_params)
            # print("Artworks Data:", artworks)
            if error or not artworks_details:
                return saved_artworks, error
            for artwork in artworks_details:
                newart = cls.filter_dates(artwork, user_century)
                if newart:
                    saved_artwork = save_artwork(artwork_detail=newart)
                    if saved_artwork:
                        saved_artworks.append(saved_artwork) 
                    if len(saved_artworks) >= total_art_for_app:
                        break

            page += 1
            query_params['page'] = page
        return saved_artworks

    @classmethod
    def surprise_me(cls, user):
        """Fetches artworks from a randomly selected unchosen century."""
        
        user_century = Century.query.get(user.century_id).century_name
        unchosen_centuries = [c for c in cls.century_dates if c != user_century]
        
        if not unchosen_centuries:
            flash("API_REQUESTS-No unchosen centuries found.", "danger")
            return None, "No unchosen centuries found."

        random_century = random.choice(unchosen_centuries)
        total_surprise = 50

        page = 1
        favorite_artwork_ids, not_favorite_artwork_ids = cls.fetch_favorite_and_not_favorite_ids(user.id)
        saved_artworks = []

        #define API parameters with filtering
        query_params = {
            'limit': 100,
            'page' : page,
            'fields': 'id,title,artist_title,image_id, dimensions,medium_display,date_display,date_start,date_end, artist_display',
            'excluded_ids': ','.join(map(str, favorite_artwork_ids + not_favorite_artwork_ids))
        }

        #fetch data until enough artworks are collected
        while len(saved_artworks) < total_surprise:
            artworks, error = cls.fetch_artworks_from_api(query_params)
            if error or not artworks:
                return saved_artworks, error  
            for artwork in artworks:
                sopresa = cls.filter_dates(artwork, random_century)
                if sopresa:
                    saved_artwork_surprise = save_artwork(artwork_detail=sopresa)
                    if saved_artwork_surprise:
                        saved_artworks.append(saved_artwork_surprise)
                    if len(saved_artworks) >= total_surprise:
                        break
                
                
            page += 1
            query_params['page'] = page

        return saved_artworks, random_century