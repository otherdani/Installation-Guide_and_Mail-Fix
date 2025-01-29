from flask import Blueprint, render_template
from models import Pet

trackers_bp = Blueprint('trackers', __name__)

TRACKERS = [
    {"name": "Weight Tracker", "description": "Track your pet's weight over time", "endpoint": "trackers.weight"},
    {"name": "Vaccination Tracker", "description": "Keep track of your pet's vaccinations", "endpoint": "trackers.vaccinations"},
    {"name": "Internal Deworming", "description": "Monitor internal deworming schedules", "endpoint": "trackers.internal_deworming"},
    {"name": "External Deworming", "description": "Track external deworming treatments", "endpoint": "trackers.external_deworming"},
    {"name": "Medication Tracker", "description": "Keep a record of medications given", "endpoint": "trackers.medications"}
]

@trackers_bp.route('/<int:pet_id>')
def trackers_home(pet_id):
    """Display trackers"""
    pet = Pet.query.get_or_404(pet_id)
    return render_template('trackers.html', pet=pet, trackers=TRACKERS)
