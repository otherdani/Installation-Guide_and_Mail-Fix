from datetime import datetime
from sqlalchemy import CheckConstraint
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
    """Pet breed"""
    __tablename__ = 'breeds'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    species = db.relationship('Species', backref=db.backref('breeds', lazy=True))

class Pet(db.Model):
    """Pet data"""
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    adoption_date = db.Column(db.Date, nullable=True)
    sex = db.Column(db.String(6), nullable=False)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False)
    breed_id = db.Column(db.Integer, db.ForeignKey('breeds.id'), nullable=True)
    sterilized = db.Column(db.Boolean, nullable=False, default=False)
    microchip_number = db.Column(db.String(50), nullable=True)
    insurance_company = db.Column(db.String(100), nullable=True)
    insurance_number = db.Column(db.String(50), nullable=True)

    breed = db.relationship('Breed', backref=db.backref('pets', lazy='joined'))
    species = db.relationship('Species', backref=db.backref('pets', lazy='joined'))

    __table_args__ = (
        CheckConstraint("sex IN ('Male', 'Female')", name='check_sex'),
    )

    # Determine pet age
    def age(self):
        if self.birth_date:
            today = datetime.today()
            age = today.year - self.birth_date.year
            # Adjust if the pet hasn't had its birthday yet this year
            if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day < self.birth_date.day):
                age -= 1
            return age
        return None
