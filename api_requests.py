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
                    favorite_artwork_ids = [fav.artwork_id for fav in Favorite.query.filter_by(user_id=user.id).all()]
                    not_favorite_artwork_ids = [not_fav.artwork_id for not_fav in NotFavorite.query.filter_by(user_id=user.id).all()]
                    
                    artworks_details = cls.filter_artworks(artworks, favorite_artwork_ids, not_favorite_artwork_ids, date_range)
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
                artworks_details = []
                for artwork in artworks:
                    date_start = int(artwork.get('date_start', 0))
                    date_end = int(artwork.get('date_end', 0))
                    date_range_start, date_range_end = map(int, date_range)
                    
                    if date_range_start <= date_start <= date_range_end or date_range_start <= date_end <= date_range_end:
                        if artwork['id'] not in favorite_artwork_ids and artwork['id'] not in not_favorite_artwork_ids:
                            artworks_details.append({
                                'id' : artwork.get('id'),
                                'title': artwork.get('title'),
                                'artist_title': artwork.get('artist_title', 'Unknown Artist'),
                                'artist_display': artwork.get('artist_display', ''),
                                'date_start': artwork.get('date_start', ''),
                                'date_end': artwork.get('date_end', ''),
                                'date_display': artwork.get('date_display', ''),
                                'medium_display': artwork.get('medium_display', ''),
                                'dimensions': artwork.get('dimensions', ''),
                                'image_id': artwork.get('image_id'),
                                'image_url': f"https://www.artic.edu/iiif/2/{artwork['image_id']}/full/843,/0/default.jpg" if artwork.get('image_id') else None
                            })
                return artworks_details 