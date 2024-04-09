from unittest import TestCase
from models import User, Century, db, Artwork, Artist
import os

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_art_views.py


#set up the environmenta database

os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

#import the app
from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

class ArtworkViewTestCase(TestCase):
    """Tests for artwork related routes"""
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
        """Set up the db with the initial data - helper method"""
        User.query.delete()
        Century.query.delete()
        Artwork.query.delete()
        c_18 = Century(century_name="18th Century")
        db.session.add(c_18)
        db.session.commit()

        Stacy = Artist(artist_title="Stacy Smith", artist_display="TAAACOS")
        Allison = Artist(artist_title="Allison Currie", artist_display="CRAWFISH")
        db.session.add_all([Stacy, Allison])
        db.session.commit()

        test_art_s = Artwork(title="Does Allison love Em more than queso?",
                           artist_id=Stacy.id, 
                           image_url = "https://chefsgarden-cdn-prod.azureedge.net/width-960-amp;height-420-amp;mode-crop-amp;-scale-both-amp;quality-80-cache-2-3/TheChefsGarden/media/TCG/Product-Detail-Images/Root/Potatoes/Potatoes-Sizing-Spoons.jpg")
        
        test_art_a = Artwork(title="Does Stacy love Em more than yellow octopus?",
                           artist_id=Allison.id, 
                           image_url = "https://chefsgarden-cdn-prod.azureedge.net/width-960-amp;height-420-amp;mode-crop-amp;-scale-both-amp;quality-80-cache-2-3/TheChefsGarden/media/TCG/Product-Detail-Images/Root/Potatoes/Potatoes-Sizing-Spoons.jpg")

        db.session.add_all([test_art_s, test_art_a])
        db.session.commit()

        self.u1 = User.signup(username="testpotato",
                              first_name="Bob",
                              last_name="taco",
                              email="test@test.com",
                              password="testuser",
                              century_id=c_18.id)
        
        db.session.add(self.u1)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()

    def test_favorites_unauthorized(self):
        """Test the favorites route without a logged-in user."""
        with app.app_context():
            with self.client as c:
                res = c.get('/users/favorites', follow_redirects=True)
                html = res.get_data(as_text=True)
            
                self.assertEqual(res.status_code, 200)
                self.assertIn("Access unauthorized.", html)


