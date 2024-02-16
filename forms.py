from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, HiddenField
from wtforms.validators import InputRequired, Length, Email, Optional

class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Length(max=50)])
    first_name = StringField("First name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last name", validators=[InputRequired(), Length(max=30)])

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
    pass
    HiddenField
    