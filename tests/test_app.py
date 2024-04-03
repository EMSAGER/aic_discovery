from unittest import TestCase
from flask import Flask, render_template, redirect, session, flash, g, request
from flask_debugtoolbar import DebugToolbarExtension
from models import User, Century
from sqlalchemy.exc import IntegrityError
from api_requests import APIRequests
from favoriting_Art import ArtworkFavorites
import random
import os

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_app.py


#set up the environmenta database

os.environ['DATABASE_URL'] = "postgresql:///test_aic_capstone"

#import the app
from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

class UserViewTestCase(TestCase):
    """Tests for user related routes"""
    def setUp(self):
        """Create test client add sample data"""
        self.client = app.test_client()
        self.app_context = app.app_context()
        with self.app_context():
            db.create_all()
            self.populate_db()
       
       
    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.remove()
        db.drop_all()

    def populate_db(self):
        """Set up the db with the initial data - helper method"""
        c_18 = Century(century_name="18th Century")
        c_19 = Century(century_name="19th Century")
        c_20 = Century(century_name="20th Century")
        db.session.add_all([c_18, c_19, c_20])
        db.session.commit()

        self.u1 = User.signup(username="testpotato",
                                    email="test@test.com",
                                    password="testuser",
                                    century_id=c_18)
        
        self.u2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    century_id=c_19)
        
        self.u3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="testuser3",
                                    century_id=c_20)
        
        db.session.add_all([self.u1, self.u2, self.u3])

        db.session.commit()

    def test_signup_route_post(self):
        """test the signup route"""
        with app.app_context():
            with self.client as c:
                res = c.post('/signup', data={
                        'username': 'newuser',
                        'password': 'password',
                        'email': 'new@example.com',
                        'first_name': 'New',
                        'last_name': 'User',
                        'century_id': 1
                    }, follow_redirects=True)
                html = res.get_data(as_text=True)

                self.assertEqual(res.status_code, 200)