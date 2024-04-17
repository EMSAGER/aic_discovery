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
    def fetch_artworks_from_api(cls, query_params):
        """Fetch artwork data from the API"""
        try:
            response = requests.get(cls.API_URL, headers=cls.HEADER, params=query_params)
            if response.status_code == 200:
                return response.json()['data'], None
            else:
                flash(f"Failed to fetch artworks from API - {{response.status_code}} ", "danger")
                return None
        except requests.RequestException as e:
                flash(f"Error connecting to the Art Institute of Chicago API: {e}", "danger") 
                return None
    
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
        date_range = cls.century_dates.get(user_century, (None, None))
        total_art_for_app = 50
        saved_artworks = []
        page = 1

        favorite_artwork_ids, not_favorite_artwork_ids = cls.fetch_favorite_and_not_favorite_ids(user.id)

        #define API parameters with filtering
        query_params = {
            'limit': 100,
            'page' : page,
            'fields': 'id,title,artist_title,image_id,dimensions,medium_display,date_display,date_start,date_end, artist_display',
            'excluded_ids': ','.join(map(str, favorite_artwork_ids + not_favorite_artwork_ids)),
            'date_start_gte': date_range[0],
            'date_end_lte': date_range[1]
        }

        #fetch data until enough artworks are collected
        while len(saved_artworks) < total_art_for_app:
            artworks, error = cls.fetch_artworks_from_api(query_params)
            if error or not artworks:
                break
            for artwork in artworks:
                if len(saved_artworks) >= total_art_for_app:
                    break
                saved_artwork = save_artwork(artwork_detail=artwork)
                if saved_artwork:
                    saved_artworks.append(saved_artwork)    
            page += 1
            query_params['page'] = page
        return saved_artworks

    @classmethod
    def surprise_me(cls, user):
        """Fetches artworks from a randomly selected unchosen century."""
        
        user_century = Century.query.get(user.century_id).century_name
        unchosen_centuries = [c for c in cls.century_dates if c != user_century]
        
        if not unchosen_centuries:
            flash("No unchosen centuries found.", "danger")
            return None, "No unchosen centuries found."

        random_century = random.choice(unchosen_centuries)
        date_range = cls.century_dates.get(random_century, (None, None))

        total_surprise = 50
        surprised_fetch = 0
        page = 1
        saved_artworks = []

        #define API parameters with filtering
        query_params = {
            'limit': 100,
            'page' : page,
            'fields': 'id,title,artist_title,image_id,dimensions,medium_display,date_display,date_start,date_end, artist_display',
            'excluded_ids': ','.join(map(str, favorite_artwork_ids + not_favorite_artwork_ids)),
            'date_start_gte': date_range[0],
            'date_end_lte': date_range[1]
        }

        #fetch data until enough artworks are collected
        while len(surprised_fetch) < total_surprise:
            artworks, error = cls.fetch_artworks_from_api(query_params)
            if error or not artworks:
                break
            for artwork in artworks:
                if len(surprised_fetch) >= total_surprise:
                    break
                saved_artwork_surprise = save_artwork(artwork_detail=artwork)
                if saved_artwork_surprise:
                    saved_artworks.append(saved_artwork_surprise)
            page += 1
            query_params['page'] = page

        return saved_artworks, random_century