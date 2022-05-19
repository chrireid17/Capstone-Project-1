from ast import In, Pass
from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, EqualTo

class SignupForm(FlaskForm):
    """Form for users to signup"""

    username = StringField('Username', validators=[InputRequired(), Length(min=6, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6), EqualTo('confirm_password', message='Passwords must match')] )
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=6)])

class LoginForm(FlaskForm):
    """Form to authenticate a user"""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
