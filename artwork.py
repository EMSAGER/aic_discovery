from models import db, Artwork, Artist
from flask import flash

def save_artwork(artwork_detail):
    
    artist = Artist.query.filter_by(artist_title=artwork_detail['artist_title']).first()
    if not artist:
        artist = Artist(artist_title=artwork_detail['artist_title'])
        db.session.add(artist)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while saving the artist: {e}", "danger")
            return None

    #check if an artwork with the provided id already exists
    artwork = Artwork.query.get(artwork_detail['id'])
    if artwork:
        artwork.title = artwork_detail['title']
        artwork.artist_id = artist.id
        artwork.date_start = artwork_detail.get('date_start')
        artwork.date_end = artwork_detail.get('date_end')
        artwork.medium_display = artwork_detail['medium_display']
        artwork.dimensions = artwork_detail['dimensions']
        artwork.image_id = artwork_detail.get('image_id')
        artwork.image_url = artwork_detail['image_url']
    else:
        artwork = Artwork(
            id = artwork_detail['id'],
            title=artwork_detail['title'],
            artist_id=artist.id,
            date_start=artwork_detail.get('date_start'),
            date_end=artwork_detail.get('date_end'),
            medium_display=artwork_detail['medium_display'],
            dimensions=artwork_detail['dimensions'],
            image_id=artwork_detail.get('image_id'),
            image_url=artwork_detail['image_url']
        )
        db.session.add(artwork)

    try:
        db.session.commit()
        return artwork
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while saving the artwork: {e}", "danger")
        return None
