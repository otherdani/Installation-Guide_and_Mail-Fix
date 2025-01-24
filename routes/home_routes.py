from flask import Blueprint, render_template
from flask_login import login_required

from helpers import login_required, inject_pets

home_bp = Blueprint('home', __name__)

@home_bp.route("/welcome")
def welcome():
    """Display Welcome page"""
    return render_template("welcome.html")

@home_bp.route('/')
@login_required
@inject_pets
def home():
    """Display homepage"""
    return render_template("index.html")
