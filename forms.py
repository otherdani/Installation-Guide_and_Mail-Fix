from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField, FileField, SelectField, PasswordField
from wtforms.validators import DataRequired, Optional, Email, EqualTo
from flask_wtf.file import FileAllowed
from models import Species, Breed

class RegisterForm(FlaskForm):
    """Register a new user"""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmation = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

class LoginForm(FlaskForm):
    """Login an existing user"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class PetForm(FlaskForm):
    """Add a new pet"""
    pet_profile_photo = FileField('Upload Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'), Optional()])
    name = StringField('Pet Name', validators=[DataRequired()])
    birth_date = DateField('Birth Date', format='%Y-%m-%d', validators=[Optional()])
    adoption_date = DateField('Adoption Date', format='%Y-%m-%d', validators=[Optional()])
    sex = SelectField('Sex', choices=[('', 'Select Sex'), ('M', 'Male'), ('F', 'Female')], validators=[DataRequired()])
    species = SelectField('Species', coerce=int, validators=[DataRequired()])
    breed = SelectField('Breed', coerce=int, validators=[DataRequired()])
    sterilized = BooleanField('Sterilized')
    microchip_number = StringField('Microchip Number', validators=[Optional()])
    insurance_company = StringField('Insurance Company', validators=[Optional()])
    insurance_number = StringField('Insurance Number', validators=[Optional()])