#tests artwork.py
#tests the code that saves artwork to the db or to a file

from unittest import TestCase
from models import User, Century, db, Artwork, Artist
import os

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_user_views.py


#set up the environmenta database

os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

#import the app
from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
