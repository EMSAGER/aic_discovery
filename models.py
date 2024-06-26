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
    century_id = db.Column(db.Integer, db.ForeignKey('centuries.id'), nullable=False)
    
    favorites = db.relationship('Favorite', backref='user')
    not_favorites = db.relationship('NotFavorite', backref='user')
    century = db.relationship('Century', backref='user')

    @property
    def full_name(self):
        """Return full name of user."""

        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def signup(cls, username, password, email, first_name, last_name, century_id):
        """Register user w/hashed password & return user."""
        if cls.query.filter_by(username=username).first():
            raise ValueError("Username already exists")
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        # return instance of user w/username and hashed pwd
        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
            first_name=first_name,
            last_name=last_name,
            century_id=century_id
        )
        db.session.add(user)
        db.session.commit()
        return user

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
    artist_title = db.Column(db.Text)
    artist_display = db.Column(db.Text)
    
    
    artworks = db.relationship('Artwork', backref='artist', cascade="all, delete-orphan",  lazy=True)


class Artwork(db.Model):
    __tablename__= 'artworks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    date_start = db.Column(db.Integer)
    date_end = db.Column(db.Integer)
    medium_display = db.Column(db.String(255))
    dimensions = db.Column(db.String(255))
    on_view = db.Column(db.Boolean, default=False)
    on_loan = db.Column(db.Boolean, default=False)
    classification_title = db.Column(db.String, db.ForeignKey('classifications.classification_title'), nullable=True)
    image_id = db.Column(db.String(255), unique=True, nullable=True) 
    image_url = db.Column(db.Text, nullable = False)
    
    classifications = db.relationship('Classification', backref='artworks', lazy=True)

    @property
    def artist_title(self):
        """returns the artist's name"""
        return self.artist.artist_title
    
    @property
    def artist_display(self):
        """If available, it returns the artist's biography"""
        return self.artist.artist_display
    
    

class Classification(db.Model):
    __tablename__ = 'classifications'
    classification_title = db.Column(db.String, primary_key=True)
    
class Favorite(db.Model):
    __tablename__= 'favorites'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)

    artist = db.relationship('Artist', backref='favorites')
    artwork = db.relationship('Artwork', backref='favorites')

class NotFavorite(db.Model):
    __tablename__ = 'not_favorites'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)

    artist = db.relationship('Artist', backref='not_favorites')
    artwork = db.relationship('Artwork', backref='not_favorites')

class Century(db.Model):
    __tablename__= 'centuries'
    id = db.Column(db.Integer, primary_key=True)
    century_name = db.Column(db.Text, unique=True, nullable=False)
    


