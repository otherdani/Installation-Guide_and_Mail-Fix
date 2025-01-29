from datetime import datetime
from extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    """User for database"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash = db.Column(db.String(120), nullable=False)

    pets = db.relationship('Pet', backref='owner', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "pets": [pet.to_dict() for pet in self.pets]
        }


class Species(db.Model):
    """Pet species"""
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "breeds": [breed.to_dict() for breed in self.breeds]
        }


class Breed(db.Model):
    """Pet breeds"""
    __tablename__ = 'breeds'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    species = db.relationship('Species', back_populates='breeds', lazy='select')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "species": {"id": self.species.id, "name": self.species.name} if self.species else None
        }


class Pet(db.Model):
    """Pet general data"""
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    pet_profile_photo = db.Column(db.String(200), nullable=True)
    name = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    adoption_date = db.Column(db.Date, nullable=True)
    sex = db.Column(db.String(1), db.CheckConstraint("sex IN ('M', 'F')"), nullable=False)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id', ondelete='CASCADE'), nullable=False, index=True)
    breed_id = db.Column(db.Integer, db.ForeignKey('breeds.id', ondelete='SET NULL'), nullable=True, index=True)
    sterilized = db.Column(db.Boolean, nullable=False, default=False)
    microchip_number = db.Column(db.String(50), unique=True, nullable=True)
    insurance_company = db.Column(db.String(100), nullable=True)
    insurance_number = db.Column(db.String(50), nullable=True)

    species = db.relationship('Species', lazy='joined')
    breed = db.relationship('Breed', lazy='joined')
    photos = db.relationship('Photo', backref='pet', lazy=True)
    logs = db.relationship('Log', backref='pet', lazy=True)

    # Inverse relationships
    Species.breeds = db.relationship('Breed', back_populates='species', lazy='select')
    Breed.pets = db.relationship('Pet', back_populates='breed', lazy='select')
    Species.pets = db.relationship('Pet', back_populates='species', lazy='select')


    def age(self):
        """Determine pet age"""
        if self.birth_date:
            today = datetime.today()
            age = today.year - self.birth_date.year
            # Adjust if the pet hasn't had its birthday yet this year
            if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day < self.birth_date.day):
                age -= 1
            return age
        return None
    
    def days_to_birthday(self, birthdate):
        """Calculate days to birthday"""
        today = datetime.today().date()
        next_birthday = birthdate.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "pet_profile_photo": self.pet_profile_photo,
            "birth_date": self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            "adoption_date": self.adoption_date.strftime('%Y-%m-%d') if self.adoption_date else None,
            "sex": self.sex,
            "species": {"id": self.species.id, "name": self.species.name} if self.species else None,
            "breed": {"id": self.breed.id, "name": self.breed.name} if self.breed else None,
            "sterilized": self.sterilized,
            "microchip_number": self.microchip_number,
            "insurance_company": self.insurance_company,
            "insurance_number": self.insurance_number,
            "age": self.age(),
            "photos": [photo.to_dict() for photo in self.photos],
            "logs": [log.to_dict() for log in self.logs]
        }


class Photo(db.Model):
    """Pet Photo"""
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(100))
    date_uploaded = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "image_url": self.image_url,
            "title": self.title,
            "date_uploaded": self.date_uploaded.strftime('%Y-%m-%d')
        }
    
class Log(db.Model):
    """Entry log"""
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    title = db.Column(db.String(150))
    date_uploaded = db.Column(db.Date, nullable=False)
    content = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "content": self.content,
            "title": self.title,
            "date_uploaded": self.date_uploaded.strftime('%Y-%m-%d')
        }
    
class WeightTracker(db.Model):
    """Database model for pet weight tracking"""
    __tablename__ = 'weight_tracker'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id', ondelete='CASCADE'), nullable=False)
    weight_in_kg = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "weight_in_kg": self.weight_in_kg,
            "date": self.date.strftime('%Y-%m-%d'),
            "notes": self.notes,
        }

class VaccineTracker(db.Model):
    """Database model for pet vaccine tracking"""
    __tablename__ = 'vaccine_tracker'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id', ondelete='CASCADE'), nullable=False)
    vaccine_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    next_dosis = db.Column(db.Date, nullable=True)
    administered_by = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "vaccine_name": self.vaccine_name,
            "date_administered": self.date.strftime('%Y-%m-%d'),
            "next_dosis": self.next_dosis.strftime('%Y-%m-%d') if self.next_dosis else None,
            "administered_by": self.administered_by,
            "notes": self.notes,
        }

class InternalDewormingTracker(db.Model):
    """Database model for internal deworming tracking"""
    __tablename__ = 'internal_deworming_tracker'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id', ondelete='CASCADE'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    next_dosis = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "product_name": self.product_name,
            "date_administered": self.date.strftime('%Y-%m-%d'),
            "next_dosis": self.next_dosis.strftime('%Y-%m-%d') if self.next_dosis else None,
            "notes": self.notes,
        }

class ExternalDewormingTracker(db.Model):
    """Database model for external deworming tracking"""
    __tablename__ = 'external_deworming_tracker'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id', ondelete='CASCADE'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    next_dosis = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "product_name": self.product_name,
            "date_administered": self.date.strftime('%Y-%m-%d'),
            "next_dosis": self.next_dosis.strftime('%Y-%m-%d') if self.next_dosis else None,
            "notes": self.notes,
        }
    
class MedicationTracker(db.Model):
    """Database model for medication tracking"""
    __tablename__ = 'medication_tracker'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id', ondelete='CASCADE'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    next_dosis = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "product_name": self.product_name,
            "date_administered": self.date.strftime('%Y-%m-%d'),
            "next_dosis": self.next_dosis.strftime('%Y-%m-%d') if self.next_dosis else None,
            "notes": self.notes,
        }