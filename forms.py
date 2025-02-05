from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField, FileField, SelectField, PasswordField, SubmitField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Optional, Email, EqualTo, Length
from flask_wtf.file import FileAllowed


# Auth Forms
class RegisterForm(FlaskForm):
    """Register a new user"""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirmation = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

class LoginForm(FlaskForm):
    """Login an existing user"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RestorePasswordForm(FlaskForm):
    """Restore Password"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    """Reset Password"""
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


# Pet Forms
class PetForm(FlaskForm):
    """Add new pet"""
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


# Features Forms
class PhotoForm(FlaskForm):
    """Pet Photos"""
    title = StringField('Title', validators=[Length(max=100), Optional()])
    image = FileField('Image', validators=[DataRequired()])
    date_uploaded = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])

class EntryForm(FlaskForm):
    """Entry Logs"""
    title = StringField('Title', validators=[Length(max=150), Optional()])
    content = TextAreaField('Content', validators=[DataRequired()])
    date_uploaded = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])


# Trackers Forms
class WeightForm(FlaskForm):
    """Form for tracking pet weight"""
    weight = FloatField('Weight (kg)', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Add Weight Entry')

class VaccineForm(FlaskForm):
    """Form for tracking pet vaccines"""
    vaccine_name = StringField('Vaccine Name', validators=[DataRequired(), Length(max=100)])
    date = DateField('Date Administered', format='%Y-%m-%d', validators=[DataRequired()])
    next_dosis = DateField('Next Dose Date', format='%Y-%m-%d', validators=[Optional()])
    administered_by = StringField('Administered By', validators=[Optional(), Length(max=150)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Add Vaccine Entry')

class InternalDewormingForm(FlaskForm):
    """Form for internal deworming tracker"""
    product_name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    date= DateField('Date Administered', format='%Y-%m-%d', validators=[DataRequired()])
    next_dosis = DateField('Next Dose Date', format='%Y-%m-%d', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Add Internal Deworming Entry')

class ExternalDewormingForm(FlaskForm):
    """Form for external deworming tracker"""
    product_name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    date = DateField('Date Administered', format='%Y-%m-%d', validators=[DataRequired()])
    next_dosis = DateField('Next Dose Date', format='%Y-%m-%d', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Add External Deworming Entry')


class MedicationForm(FlaskForm):
    """Form for medication tracker"""
    product_name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    date = DateField('Date Administered', format='%Y-%m-%d', validators=[DataRequired()])
    next_dosis = DateField('Next Dose Date', format='%Y-%m-%d', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Add Medication Entry')