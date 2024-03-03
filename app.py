from flask import Flask, render_template, redirect, session, flash, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Favorite, Artwork, Century, NotFavorite
from forms import UserEditForm, UserForm, LoginForm, FavoriteForm
from sqlalchemy.exc import IntegrityError
from api_requests import APIRequests
from favoriting_Art import ArtworkFavorites
import random
import os
from dotenv import load_dotenv


load_dotenv()

CURR_USER_KEY = "curr_user"
API_URL = "https://api.artic.edu/api/v1/artworks/search"
HEADER = {
    'AIC-User-Agent': 'AIC Discovery (emsager7@gmail.com)'
}

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

connect_db(app)
toolbar = DebugToolbarExtension(app)

favorite = favoriting_Art.ArtworkFavorites
##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def initialize_app():
    initialize_centuries()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def initialize_centuries():
    if not Century.query.first():
        centuries = ['18th Century', '19th Century', '20th Century']
        for name in centuries:
            if not Century.query.filter_by(century_name=name).first():
                century = Century(century_name=name)
                db.session.add(century)
        db.session.commit()

@app.context_processor
def inject_user():
    """This function will run before templates 
    are rendered and will inject the user variable 
    into the context of all templates, making it 
    unnecessary to manually pass the user variable in 
    each render_template call.

"""
    return dict(user=g.user)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    initialize_centuries()
    form = UserForm()
    form.century_id.choices = [(c.id, c.century_name)for c in Century.query.order_by('id')]
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                century_id=form.century_id.data  
            )
            db.session.add(user)
            db.session.commit()
            do_login(user)
            # flash("User successfully registered.", 'success')
            return redirect('/users/profile') 
        
        except IntegrityError:
            db.session.rollback()
            flash("Username already taken", 'danger')
    
    return render_template('/users/signup.html', form=form)
            
@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            # flash(f"Hello, {user.full_name}!", "success")
            return redirect("/users/profile")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    if 'curr_user' in session:
        del session['curr_user']
    flash("Goodbye!", "primary")
    return redirect('/login')

##############################################################################
# User focused routes

@app.route('/users/profile')
def user_profile():
    """Returns the user's profile page
    This route will also communicate with the API server to pull an image filtered by the century picked"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = FavoriteForm()
    user = g.user
    user_century = Century.query.get(user.century_id).century_name

    saved_artworks = APIRequests.get_artworks(user)

    selected_artwork = random.choice(saved_artworks) if saved_artworks else None
    
    return render_template('/users/profile.html', selected_artwork=selected_artwork, user=user, century = user_century, form=form)

@app.route('/users/profile/edit', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    form = UserEditForm(obj=user)
    form.century_id.choices = [(c.id, c.century_name) for c in Century.query.order_by('century_name')]
    if form.validate_on_submit():
        auth_user = User.authenticate(user.username, form.password.data)
        if auth_user:
            user.username = form.username.data
            user.email = form.email.data
            user.century_id = form.century_id.data
            db.session.commit()
            # flash("User Updated!", "success")
            return redirect(f"/users/profile")
        else:
            # If authentication fails, flash an error message
            flash("Incorrect password.", "danger")
            return render_template("users/edit.html", user=user, form=form)
  
    
    return render_template("users/edit.html", user=user, form=form)

##############################################################################
# Art focused routes
@app.route('/users/favorites/<int:artwork_id>', methods=["GET", "POST"])
def favorite_artwork(artwork_id):
    """Favorites an image. It checks to make sure the image isn't liked beforehand.
    If not, it is added to the favorites table & redirected to the page"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user

    result, status = ArtworkFavorites
    # artwork = Artwork.query.get(artwork_id)
    # if not artwork:
    #     flash("Artwork not found.", "danger")
    #     return redirect("/users/profile")
    
    # existing_favorite = Favorite.query.join(Artwork, Favorite.artwork_id == Artwork.id).filter(Artwork.image_id == artwork.image_id).first()

    # if existing_favorite:
    #     flash("This artwork is already in your favorites.", "warning")
    #     return redirect("/users/profile")
    
    # artist_id = artwork.artist_id
    # favorite = Favorite.query.filter_by(user_id=user, artwork_id=artwork_id, artist_id = artist_id).first()
    # if favorite:
    #     #removes the favorite tag -- does not dislike
    #     db.session.delete(favorite)
    #     flash("Artwork removed from favorites.", "warning")
    # else:
    #     new_favorite = Favorite(user_id=user, artwork_id=artwork_id, artist_id=artist_id)
    #     db.session.add(new_favorite)
    #     flash("Artwork added to favorites.", "success")

    # db.session.commit()    
    # return redirect('/users/profile')
    
@app.route('/users/favorites')
def all_favorites():
    """Retrieves all of the current user's favorited works"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    # Retrieve all favorites for the current user and join with Artwork to get details
    favorites = (db.session.query(Favorite, Artwork)
                 .join(Artwork)
                 .filter(Favorite.artwork_id == Artwork.id)
                 .all())
    
    seen = set()
    favorite_artworks = []
    for fav in favorites:
        if fav.Artwork.image_id not in seen:
            seen.add(fav.Artwork.image_id)
            favorite_artworks.append({'id': fav.Artwork.id,
                          'title': fav.Artwork.title,
                          'image_id': fav.Artwork.image_id,
                          'artist_title': fav.Artwork.artist_title,
                          'date_start': fav.Artwork.date_start,
                          'date_end': fav.Artwork.date_end,
                          'image_url': f"https://www.artic.edu/iiif/2/{fav.Artwork.image_id}/full/843,/0/default.jpg"})
    
    return render_template('/favorites/favorites.html', favorites=favorite_artworks)

@app.route('/users/not_favorites/<int:artwork_id>', methods=["GET", "POST"])
def not_favorite_image(artwork_id):
    """Puts the unliked image into it's own category so that a user won't see it again"""
    if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/users/profile")
        
    user = g.user.id
    artwork = Artwork.query.get(artwork_id)
    if not artwork:
        flash("Artwork not found.", "danger")
        return redirect("/users/profile")
    
    existing_not_favorite = NotFavorite.query.join(Artwork, NotFavorite.artwork_id == Artwork.id).filter(Artwork.image_id == artwork.image_id).first()

    if existing_not_favorite:
        flash("This artwork is already in your favorites.", "warning")
        return redirect("/users/profile")
    
    artist_id = artwork.artist_id
    not_favorite = NotFavorite.query.filter_by(user_id=user, artwork_id=artwork_id, artist_id = artist_id).first()
    if not_favorite:
        #removes the favorite tag -- does not dislike
        db.session.delete(not_favorite)
        flash("Dislike removed.", "success")
    else:
        new_not_favorite = NotFavorite(user_id=user, artwork_id=artwork_id, artist_id=artist_id)
        db.session.add(new_not_favorite)
        flash("Artwork disliked.", "success")

    db.session.commit()    
    return redirect('/users/profile')

##############################################################################
# Surprise Me Routes
"""the purpose of these routes is to 
show users artwork from the centuries they didn't chose."""
@app.route('/users/surprise', methods=['POST', 'GET'])
def suprise_home():
    """Route that shows the suprise page and showcases artwork from unchosen centuries"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    form = FavoriteForm()
    user = g.user
    
    artworks_details, random_century = APIRequests.suprise_me(user)

    if artworks_details:
        artwork_to_display = random.choice(artworks_details) if artworks_details else None
        return render_template('/artwork/surprise.html', artwork=artwork_to_display, user=user, form=form, century=random_century)
    else:
        flash("Failed to fetch artworks from the API.", "danger")
        redirect('/users/suprise')
    
    
##############################################################################
# Homepage

@app.route('/')
def home_page():
    return render_template('index.html')


