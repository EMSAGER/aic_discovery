from flask import Flask, render_template, redirect, session, flash, g, request
from flask_debugtoolbar import DebugToolbarExtension
from  models import db, User, Favorite, Artwork, Century
from  forms import UserEditForm, UserForm, LoginForm, FavoriteForm
from sqlalchemy.exc import IntegrityError
from  api_requests import APIRequests
from  favoriting_Art import ArtworkFavorites
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


toolbar = DebugToolbarExtension(app)

fav_artwork = ArtworkFavorites.fav_artwork
dislike_artwork = ArtworkFavorites.dislike_artwork
unfavorite_artwork = ArtworkFavorites.unfavorite_artwork
##############################################################################
# User signup/login/logout

with app.app_context():
        db.app = app
        db.init_app(app)
        db.create_all()


@app.before_request
def initialize_app():
    """initiailiaze application & create necessary directories"""
    create_directories()
    add_user_to_g()
    


def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def create_directories():
    """Create the necessary directories to save favorited images"""
    IMAGES_DIR_PATH = os.path.join(app.static_folder, 'images')
    if not os.path.exists(IMAGES_DIR_PATH):
        os.makedirs(IMAGES_DIR_PATH)

def login_user(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


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
            login_user(user)
            # flash("User successfully registered.", 'success')
            return redirect('/users/profile') 
        
        except ValueError:
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
            login_user(user)
            # flash(f"Hello, {user.full_name}!", "success")
            return redirect("/users/profile")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    flash("Goodbye!", "primary")
    return redirect('/login')

##############################################################################
# User focused routes

@app.route('/users/profile', methods=["GET", "POST"])
def user_profile():
    """Returns the user's profile page
    This route will also communicate with the API server to pull an image filtered by the century picked"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user

    if request.method == 'POST':
        artwork_id = request.form.get('artwork_id')
        action = request.form.get('action')

        if action == 'favorite':
            fav_artwork(user, artwork_id)
        elif action == 'not_favorite':
            dislike_artwork(user, artwork_id)
        #redirect to avoid resubmission 
        return redirect('/users/profile')

    form = FavoriteForm()
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

@app.route('/users/favorites', methods=["GET", "POST"])
def all_favorites():
    """Retrieves all of the current user's favorited works"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    
    # Retrieve all favorites for the current user and join with Artwork to get details
    user = g.user
    form = FavoriteForm()

    if request.method == 'POST':
        artwork_id = request.form.get('artwork_id')
        action = request.form.get('action')

        if action == 'favorite':
            fav_artwork(user, artwork_id)
        elif action == 'not_favorite':
            unfavorite_artwork(user, artwork_id)
        #redirect to avoid resubmission 
        return redirect('/users/favorites')


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
            
    return render_template('/users/favorites.html', favorites=favorite_artworks, form=form)

# Surprise Me Routes
"""the purpose of these routes is to 
show users artwork from the centuries they didn't chose."""
@app.route('/users/surprise', methods=['POST', 'GET'])
def surprise_home():
    """Route that shows the surprise page and showcases artwork from unchosen centuries"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    form = FavoriteForm()

    if request.method == 'POST':
        artwork_id = request.form.get('artwork_id')
        action = request.form.get('action')

        if action == 'favorite':
            res = fav_artwork(user, artwork_id)
            if res == 201:
                db.session.commit()
        elif action == 'not_favorite':
            unfavorite_artwork(user, artwork_id)
            db.session.commit()

        #redirect to avoid resubmission 
        return redirect('/users/surprise')

    artworks_details, random_century = APIRequests.surprise_me(user)

    if artworks_details:
        artwork = random.choice(artworks_details)
        return render_template('/users/surprise.html', artwork=artwork, user=user, form=form, century=random_century)
    
    else:
        flash("Failed to fetch SURPRISE data.", "danger")
        return redirect('/users/profile')
    
    
##############################################################################
# Homepage

@app.route('/')
def home_page():
    return render_template('index.html')


