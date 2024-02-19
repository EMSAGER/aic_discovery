from flask import Flask, render_template, redirect, session, flash, g, jsonify
import requests
import random
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Favorite, Artist, Artwork, Artwork_Classification, Classification, Century
from forms import UserEditForm, UserForm, LoginForm, FavoriteForm, UserEditForm
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = "curr_user"
API_URL = "https://api.artic.edu/api/v1/artworks/search"
HEADER = {
    'AIC-User-Agent': 'AIC Discovery (emsager7@gmail.com)'
}

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///aic_capstone"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "cacawsdfqwgvbqfrv5741trfgr3g4b"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False



connect_db(app)
toolbar = DebugToolbarExtension(app)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]




@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if not Century.query.first():
        centuries = ['19th Century', '20th Century', '21st Century']
        for name in centuries:
            if not Century.query.filter_by(century_name=name).first():
                century = Century(century_name=name)
                db.session.add(century)
            db.session.commit()
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
            flash("User successfully registered.", 'success')
            return render_template("/users/profile")
        
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
            flash(f"Hello, {user.full_name}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    session.pop('curr_user', None)
    flash(f"Goodbye!", "primary")
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
    
    user = User.query.get(session['curr_user']) 
    user_century = Century.query.get(g.user.century_id).century_name
    century_dates = {
        '19th Century': '1801 TO 1899',
        '20th Century': '1901 TO 1999',
        '21st Century': '2001 TO 2099',
    }
    date_range = century_dates.get(user_century)
    if date_range:
        query_params = {
            'q': f'date_start:{date_range}',
            'limit': 10,
            'fields': 'id,title,image_id,dimensions,medium_display,artist_title'  # Adjust fields as needed
        }
        try:
            response = requests.get(API_URL, headers=HEADER, params=query_params)
            res_data = response.json()
            artworks = res_data.get('data', [])
            if artworks:
                selected_artwork = random.choice(artworks)
                image_id = selected_artwork['image_id']
                image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
            else:
                image_url = None
                flash("No artwork found for the selected century.", "warning")
        except requests.RequestException:
            image_url = None
            flash("Error connecting to the Art Institute of Chicago API.", "danger")
    else:
        image_url = None
        flash("Invalid century selection.", "danger")
    return render_template("users/profile.html", user=g.user, image_url=image_url)

@app.route('/users/profile/edit', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get(session['curr_user']) 
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        auth_user = User.authenticate(username=user.username, password=form.password.data)
        if auth_user:
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            flash("User Updated!", "success")
            return redirect(f"/users/{user.id}")
        else:
            # If authentication fails, flash an error message
            flash("Incorrect password.", "danger")
            return render_template("users/edit.html", user=user, form=form)
    else:
        return render_template("users/edit.html", user=user, form=form)
    

##############################################################################
# Homepage

@app.route('/')
def home_page():
    return render_template('index.html')
