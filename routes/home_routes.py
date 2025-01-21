from flask import Blueprint, render_template, session

from models import Pet
from helpers import login_required

home_bp = Blueprint('home', __name__)

@home_bp.route("/welcome")
def welcome():
    """Display Welcome page"""
    return render_template("welcome.html")

@home_bp.route('/')
@login_required
def home():
    """Display homepage"""
    pets = Pet.query.filter_by(user_id=session["user_id"]).all()
    return render_template("index.html", pets=pets)
