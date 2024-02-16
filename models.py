from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    
    favorites = db.relationship('Favorite', backref='users')

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_title = db.Column(db.String(50), nullable = False)
    alt_title = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)
    description = db.Column(db.String(255))
    
    artworks = db.relationship('Artwork',  cascade="all,delete", backref='artist', lazy=True)

class Artwork(db.Model):
    __tablename__= 'artworks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    edu_material = db.Column(db.Boolean, default=False)
    date_start = db.Column(db.Date)
    date_end = db.Column(db.Date)
    artist_display = db.Column(db.String(255))
    dimensions = db.Column(db.String(255))
    on_view = db.Column(db.Boolean, default=False)
    on_loan = db.Column(db.Boolean, default=False)
    classification_id = db.Column(db.String, db.ForeignKey('classification.name'))
    image_id = db.Column(db.String(255))
    
    classification = db.relationship('Classification', backref='artworks', lazy=True)

class Classification(db.Model):
    __tablename__ = 'classification'
    name = db.Column(db.String, primary_key=True)
    artwork_classification = db.relationship('Artwork', backref='classification', lazy=True)

class Artwork_Classification(db.Model):
    __tablename__ = 'artwork_classification'
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), primary_key=True)
    classification_name = db.Column(db.String, db.ForeignKey('classification.name'), primary_key=True)
    artwork = db.relationship('Artwork', backref=db.backref('artwork_classifications', cascade="all, delete-orphan"), lazy=True)


class Favorites(db.Model):
    __tablename__= 'favorites'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """
    with app.app_context():
        db.app = app
        db.init_app(app)
        db.create_all()
