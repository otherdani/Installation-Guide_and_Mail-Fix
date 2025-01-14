from datetime import datetime
from app import db 

class User(db.Model):
    """User for database"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash = db.Column(db.String(120), nullable=False)

class Breed(db.Model):
    __tablename__ = 'breeds'
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, unique=True)

    species = db.relationship('Species', backref=db.backref('breeds', lazy=True))

class Species(db.Model):
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    breed_id = db.Column(db.Integer, db.ForeignKey('breeds.id'))
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'))
    birth_date = db.Column(db.Date)
    sex = db.Column(db.String(10))
    # Otros campos como foto, microchip, etc.
    
    user = db.relationship('User', backref=db.backref('pets', lazy=True))
    breed = db.relationship('Breed', backref=db.backref('pets', lazy=True))
    species = db.relationship('Species', backref=db.backref('pets', lazy=True))
    
    def age(self):
        if self.birth_date:
            today = datetime.today()
            age = today.year - self.birth_date.year
            # Adjust if the pet hasn't had its birthday yet this year
            if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day < self.birth_date.day):
                age -= 1
            return age
        return None