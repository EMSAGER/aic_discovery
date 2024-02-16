from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, HiddenField, SelectMultipleField
from wtforms.validators import InputRequired, Length, Email, Optional

favorites = [("AfD","African Diaspora"),("Anc", "Ancient"),("An", "Animals"),
             ("Arc", "Architecture"), ("ArA", "Arms and Armor"),("AD", "Art Deco"), 
             ("CA", "Chicago Artists"), ("Cty", "Cityscapes"), ("DD", "Drinking and Dining"), 
             ("Es", "Essentials"), ("Fash", "Fashion"), ("Fu", "Furniture"), ("Imp", "Impressionism"), 
             ("LS", "Landscapes"), ("Ma", "Masks"), ("Mi", "Miniature"), ("Mo", "Modernism"),("Myth", "Mythology"), 
             ("PA", "Pop Art"), ("Po", "Portraits"), ("SL", "Still Life"), ("Sur", "Surrealism"), ("WP", "Woodblock Print"), 
             ("19c", "19th Century"), ("20c", "20th Century"), ("21c", "21st Century")]

class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Length(max=50)])
    first_name = StringField("First name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last name", validators=[InputRequired(), Length(max=30)])
    favorites = SelectMultipleField("Favorites", choices=favorites, validators=[Optional()])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])


class UserEditForm(FlaskForm):
    """Form for editing users"""
    username = StringField('Username')
    email = StringField('E-mail',validators=[Optional(), Email(message='Invalid email')])
    password = PasswordField('Password')
    
class FavoriteForm(FlaskForm):
    """the purpose of this form is to pass CSRF TOKEN through"""
    csrf_token = HiddenField()
    