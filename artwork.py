#This page is for saving the artwork. Either to the DB or to a file (for the image)

from models import db, Artwork, Artist
from flask import current_app, flash
import os
import requests

class SaveArtwork:
    @classmethod
    def save_artwork(cls, artwork_detail):
        """This function saves the artwork details to the db"""
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
            #updates
            artwork.title = artwork_detail['title']
            artwork.artist_id = artist.id
            artwork.date_start = artwork_detail.get('date_start')
            artwork.date_end = artwork_detail.get('date_end')
            artwork.medium_display = artwork_detail['medium_display']
            artwork.dimensions = artwork_detail['dimensions']
            artwork.image_id = artwork_detail.get('image_id')
            artwork.image_url = artwork_detail['image_url']
        else:
            #creates a new entry
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
        
    @classmethod
    def save_image_file(cls, image_url, image_id, title):
        """Download the image from `image_url` and save it to the static/images directory""" 
        #build the path to the images directory
        IMAGES_DIR = os.path.join(current_app.static_folder, 'images')
        #ensure the directory exists
        os.makedirs(IMAGES_DIR, exist_ok=True)
        #create the full path definition
        image_path = os.path.join(IMAGES_DIR, f"{title.replace(' ', '_')}_{image_id}.jpg")

        try:
            #attempt to download
            res = requests.get(image_url)
            if res.status_code == 200:
                #write the image data to a new file
                if not os.path.exists(image_path):
                    with open(image_path, 'wb') as image_file:
                        image_file.write(res.content)
                        flash("Images successfully saved.", "success")
        except Exception as e:
            flash("Failed to download image", "danger")