from functools import wraps
from flask import redirect, session, render_template, g
from models import Pet

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


from flask import render_template

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