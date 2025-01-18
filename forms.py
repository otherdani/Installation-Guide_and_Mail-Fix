from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField, FileField, SelectField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileAllowed

class PetForm(FlaskForm):
    """Form to register a new pet"""
    pet_profile_photo = FileField('Upload Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'), Optional()])
    name = StringField('Pet Name', validators=[DataRequired()])
    birth_date = DateField('Birth Date', format='%Y-%m-%d', validators=[Optional()])
    adoption_date = DateField('Adoption Date', format='%Y-%m-%d', validators=[Optional()])
    sex = SelectField('Sex', choices=[('M'), ('F')], validators=[DataRequired()])
    species = SelectField('Species', coerce=int, validators=[DataRequired()])
    breed = SelectField('Breed', coerce=int, validators=[DataRequired()])
    sterilized = BooleanField('Sterilized')
    microchip_number = StringField('Microchip Number', validators=[Optional()])
    insurance_company = StringField('Insurance Company', validators=[Optional()])
    insurance_number = StringField('Insurance Number', validators=[Optional()])