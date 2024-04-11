#user -- century
#favorite & not favorite artowrk
###this should handle the response requests
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
    def get_artworks(cls, user):
        user_century = Century.query.get(user.century_id).century_name
        date_range = cls.century_dates.get(user_century, (None, None))
        total_art_for_app = 50
        art_fetched = 0
        page = 1
        favorite_artwork_ids = [fav.artwork_id for fav in Favorite.query.filter_by(user_id=user.id).all()]
        not_favorite_artwork_ids = [not_fav.artwork_id for not_fav in NotFavorite.query.filter_by(user_id=user.id).all()]
        saved_artworks = []
        while art_fetched < total_art_for_app:
            query_params = {
                'limit': 100,
                'page' : page,
                'fields': 'id,title,artist_title,image_id,dimensions,medium_display,date_display,date_start,date_end, artist_display'
            }
            
            try:
                response = requests.get(cls.API_URL, headers=cls.HEADER, params=query_params)
               
                if response.status_code == 200:
                    res_data = response.json()
                    artworks = res_data.get('data', [])
                   
                    
                    artworks_details = cls.filter_artworks(artworks, favorite_artwork_ids, not_favorite_artwork_ids, date_range)
                    if not artworks_details:
                        break
                    for artwork in artworks_details:
                        if art_fetched >= total_art_for_app:
                            break
                        saved_artwork = save_artwork(artwork_detail=artwork)
                        if saved_artwork:
                            saved_artworks.append(saved_artwork)
                            art_fetched += 1
                            
                else:
                    flash("Failed to fetch artworks from the API", "danger")
                    break
                
            except requests.RequestException as e:
                flash(f"Error connecting to the Art Institute of Chicago API: {e}", "danger")
                break
        
            page +=1
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

        while surprised_fetch < total_surprise:
            query_params = {
                'limit': 100,
                'page' : page,
                'fields': 'id,title,artist_title,image_id,dimensions,medium_display,date_display,date_start,date_end, artist_display, on_view, on_loan'
            }
            
            try:
                response = requests.get(cls.API_URL, headers=cls.HEADER, params=query_params)
                if response.status_code == 200:
                    res_data = response.json()
                    artworks = res_data.get('data', [])
                    favorite_artwork_ids = [fav.artwork_id for fav in Favorite.query.filter_by(user_id=user.id).all()]
                    not_favorite_artwork_ids = [not_fav.artwork_id for not_fav in NotFavorite.query.filter_by(user_id=user.id).all()]
                    
                    artworks_details = cls.filter_artworks(artworks, favorite_artwork_ids, not_favorite_artwork_ids, date_range)
                    for artwork in artworks_details:
                        if surprised_fetch >= total_surprise:
                            break
                        saved_artwork = save_artwork(artwork_detail=artwork)
                        if saved_artwork:
                            saved_artworks.append(saved_artwork)
                            surprised_fetch +=1
                            
                    
                else:
                    flash("Failed to fetch artworks from the API", "danger")
                    break
                
            except requests.RequestException as e:
                flash(f"Error connecting to the Art Institute of Chicago API: {e}", "danger")
                break
            
            page += 1
        return saved_artworks, random_century
        
    @classmethod
    def filter_artworks(cls, artworks, favorite_artwork_ids, not_favorite_artwork_ids, date_range):
        """this class method will filter the artwork so that only the images that are not favorited or unliked and within the date range will be shown"""
        artworks_details = []
        for artwork in artworks:
            #check if artwork is within the date range and is NOT favorited or unfavorited
            if (date_range[0] <= artwork.date_start <= date_range[1] or date_range[0] <= artwork.date_end <= date_range[1]) and \
            artwork.id not in favorite_artwork_ids and artwork.id not in not_favorite_artwork_ids:
                artwork_detail = {
                    'id': artwork.id,
                    'title': artwork.title,
                    'artist_title': artwork.artist_title,
                    'artist_display': artwork.artist_display,
                    'date_start': artwork.date_start,
                    'date_end': artwork.date_end,
                    'date_display': artwork.date_display(),
                    'medium_display': artwork.medium_display,
                    'dimensions': artwork.dimensions,
                    'image_id': artwork.image_id,
                    'image_url': artwork.image_url
                }
                artworks_details.append(artwork_detail)
        return artworks_details
                    