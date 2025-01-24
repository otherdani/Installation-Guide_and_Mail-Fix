from datetime import datetime
from extensions import db

class User(db.Model):
    """User for database"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash = db.Column(db.String(120), nullable=False)

    pets = db.relationship('Pet', backref='owner', lazy=True)

class Species(db.Model):
    """Pet species"""
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Breed(db.Model):
    """Pet breeds"""
    __tablename__ = 'breeds'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    species = db.relationship('Species', back_populates='breeds', lazy='select')

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