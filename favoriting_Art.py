from models import Artwork, Favorite, NotFavorite, db
from flask import flash

class ArtworkFavorites:
    @classmethod
    def fav_artwork(cls, user, artwork_id):
        """Favorites artwork for a user"""
        if not user:
            return {"error": "Access unauthorized."}, 403
        
        artwork = Artwork.query.get(artwork_id)
        if not artwork:
            return {"error": "Artwork not found."}, 404
        
        if not artwork.artist_id:
            return {"error": "Artwork must have an associated artist."}, 400

        existing_favorite = Favorite.query.filter_by(
            user_id=user.id, artwork_id=artwork_id, artist_id=artwork.artist_id).first()
        if existing_favorite:
           return {"message": "This artwork is already in your favorites"}, 200
        
        new_favorite = Favorite(user_id=user.id, artwork_id=artwork_id, artist_id=artwork.artist_id)
        db.session.add(new_favorite)
        db.session.commit()
        return {"message": "Artwork added to favorites"}, 201
    
    @classmethod
    def dislike_artwork(cls, user, artwork_id):
        """Dislike an artwork"""
        if not user:
            return {"error": "Access unauthorized."}, 403

        artwork = Artwork.query.get(artwork_id)
        if not artwork:
            return {"error": "Artwork not found."}, 404

        if not artwork.artist_id:
            return {"error": "Missing artist_id for artwork."}, 400

        existing_not_favorite = NotFavorite.query.filter_by(user_id=user.id, artwork_id=artwork_id, artist_id=artwork.artist_id).first()
        if existing_not_favorite:
            return {"message": "You already disliked this image"}, 200

        # If it's not already disliked, create a new NotFavorite
        new_not_favorite = NotFavorite(user_id=user.id, artwork_id=artwork_id, artist_id=artwork.artist_id)
        db.session.add(new_not_favorite)
        db.session.commit()
        return {"message": "Artwork disliked"}, 201
        
    @classmethod
    def unfavorite_artwork(cls, user, artwork_id):
        """Removes an artwork from the user's favorites."""
        if not user:
            return {"error": "Access unauthorized"}, 403

        favorite = Favorite.query.filter_by(user_id=user.id, artwork_id=artwork_id).first()
        if not favorite:
            return {"error": "Favorite not found"}, 404

        db.session.delete(favorite)
        db.session.commit()
        return {"message": "Artwork removed from favorites"}, 200
      
  