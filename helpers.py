import os
import base64
from io import BytesIO
from functools import wraps
from flask import redirect, session, render_template, g, current_app
from models import Pet
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

PHOTO_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/welcome")
        return f(*args, **kwargs)

    return decorated_function


def inject_pets(f):
    """Obtain pets related to a user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        pets = Pet.query.filter_by(user_id=session.get("user_id")).all()
        g.pets = pets
        return f(*args, **kwargs)
    return decorated_function


def error_message(message, code):
    """Render message as an apology to user with an http.cat image."""
    return render_template(
        "error.html",
        top=code,
        bottom=message,
    ), code


def allowed_photo_file(filename):
    """Allowed extensions for photos"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in PHOTO_ALLOWED_EXTENSIONS


def delete_pet_from_db(pet, db):
    """Helper function to delete a pet and all its associated data."""
    # Delete the pet's profile photo
    if pet.pet_profile_photo:
        pet_photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pet.pet_profile_photo)
        if os.path.exists(pet_photo_path):
            os.remove(pet_photo_path)
    
    # Delete gallery photos associated with the pet
    for photo in pet.photos:
        if photo.image_url:
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.image_url)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        db.session.delete(photo)
    
    # Delete logs, weight tracks, vaccines, medications, and deworming
    if pet.logs:
        for log in pet.logs:
            db.session.delete(log)
    if pet.weight_tracks:
        for weight in pet.weight_tracks:
            db.session.delete(weight)
    if pet.vaccines:
        for vaccine in pet.vaccines:
            db.session.delete(vaccine)
    if pet.internal_deworm:
        for deworm in pet.internal_deworm:
            db.session.delete(deworm)
    if pet.external_deworm:
        for deworm in pet.external_deworm:
            db.session.delete(deworm)
    if pet.medications:
        for medication in pet.medications:
            db.session.delete(medication)
    
    # Finally, delete the pet itself
    db.session.delete(pet)

def create_weight_graph(dates, weights, title, xlabel, ylabel, color, valid_labels=None, show_days_only=False):
    """Helper function to create and save a weight graph."""
    fig, ax = plt.subplots()
    
    if weights:  # Avoid plotting if there are no entries
        ax.plot(dates, weights, marker='o', color=color)
        
        ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
        
        # Format x-axis
        if show_days_only:
            # Use DateFormatter to show only the day of the month
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
            ax.set_xticks(dates)  # Set ticks for all days in the month
            plt.xticks(rotation=45)  # Rotate for readability

        ax.grid()

        # Save plot to a PNG image in memory
        img = BytesIO()
        fig.savefig(img, format='png')
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode('utf-8')
    
    return None  # Return None if there are no weights to plot

