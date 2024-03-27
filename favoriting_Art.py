from models import Artwork, Favorite, NotFavorite, db
from artwork import SaveArtwork

save_image = SaveArtwork.save_image_file

class ArtworkFavorites:
    NO_USER = 403
    NO_ARTWORK = 404
    NO_ARTIST_ID = 400
    @classmethod
    def fav_artwork(cls, user, artwork_id):
        """Favorites artwork for a user"""
        if not user:
                #using the syntax of the language to make the code more linguistic
            return cls.NO_USER

        artwork = Artwork.query.get(artwork_id)
        if not artwork:
            return cls.NO_ARTWORK

        if not artwork.artist_id:
            return cls.NO_ARTIST_ID

        existing_favorite = Favorite.query.filter_by(
            user_id=user.id, artwork_id=artwork_id, artist_id=artwork.artist_id).first()
        if existing_favorite:
           return 200
        
        new_favorite = Favorite(user_id=user.id, artwork_id=artwork_id, artist_id=artwork.artist_id)
        db.session.add(new_favorite)
        db.session.commit()

        #save artwork image
        if artwork.image_url and artwork.image_id:
            save_image(artwork.image_url, artwork.image_id, artwork.title)
        return  201
    

    @classmethod
    def dislike_artwork(cls, user, artwork_id):
        """Dislike an artwork"""
        if not user:
                #using the syntax of the language to make the code more linguistic
            return cls.NO_USER

        artwork = Artwork.query.get(artwork_id)
        if not artwork:
            return cls.NO_ARTWORK

        if not artwork.artist_id:
            return cls.NO_ARTIST_ID

        existing_not_favorite = NotFavorite.query.filter_by(user_id=user.id, artwork_id=artwork_id, artist_id=artwork.artist_id).first()
        if existing_not_favorite:
            return 200

        # If it's not already disliked, create a new NotFavorite
        new_not_favorite = NotFavorite(user_id=user.id, artwork_id=artwork_id, artist_id=artwork.artist_id)
        db.session.add(new_not_favorite)
        db.session.commit()
        return 201
        
    @classmethod
    def unfavorite_artwork(cls, user, artwork_id):
        """Removes an artwork from the user's favorites."""
        if not user:
            return cls.NO_USER

        favorite = Favorite.query.filter_by(user_id=user.id, artwork_id=artwork_id).first()
        if not favorite:
            return cls.NO_ARTWORK

        db.session.delete(favorite)
        db.session.commit()
        return 200
      
  