from io import BytesIO
import base64
from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
import matplotlib.pyplot as plt

from helpers import login_required, inject_pets, error_message
from models import Pet, WeightTracker, VaccineTracker, InternalDewormingTracker, ExternalDewormingTracker, MedicationTracker
from forms import WeightForm, VaccineForm, InternalDewormingForm, ExternalDewormingForm, MedicationForm

trackers_bp = Blueprint('trackers', __name__)

TRACKER_MODELS = {
    "weight": (WeightTracker, WeightForm),
    "vaccine": (VaccineTracker, VaccineForm),
    "internal_deworming": (InternalDewormingTracker, InternalDewormingForm),
    "external_deworming": (ExternalDewormingTracker, ExternalDewormingForm),
    "medication": (MedicationTracker, MedicationForm),
}

@trackers_bp.route('/<int:pet_id>')
@login_required
@inject_pets
def trackers_home(pet_id):
    """Display trackers"""
    pet = Pet.query.get_or_404(pet_id)
    
    trackers_with_entries = []
    
    for tracker_type, (model, form_class) in TRACKER_MODELS.items():
        entries = model.query.filter_by(pet_id=pet.id).order_by(model.date.desc()).limit(10).all()
        
        tracker = {
            "name": tracker_type.replace('_', ' ').title() + " Tracker",
            "description": f"Keep track of your pet's {tracker_type.replace('_', ' ')}",
            "entries": entries,
            "endpoint": f"trackers.{tracker_type}",
            "type": tracker_type
        }
        
        trackers_with_entries.append(tracker)
    
    return render_template('trackers.html', pet=pet, trackers=trackers_with_entries)

@trackers_bp.route('/add/<tracker_type>/<int:pet_id>', methods=['GET', 'POST'])
@login_required
@inject_pets
def add_tracker(tracker_type, pet_id):
    """Add new data to tracker"""
    db = current_app.extensions['sqlalchemy']

    # Form instances
    form = None
    tracker_model = None

    # Map tracker types to respective forms and models
    tracker_map = {
        'weight': (WeightForm, WeightTracker),
        'vaccine': (VaccineForm, VaccineTracker),
        'internal_deworming': (InternalDewormingForm, InternalDewormingTracker),
        'external_deworming': (ExternalDewormingForm, ExternalDewormingTracker),
        'medication': (MedicationForm, MedicationTracker)
    }

    # Check if the tracker type is valid
    if tracker_type not in tracker_map:
        return error_message("Invalid tracker type", 400)

    form_class, tracker_model = tracker_map[tracker_type]
    form = form_class()

    # Process the form if it's submitted
    if form.validate_on_submit():
        date = form.date.data
        notes = form.notes.data

        # Prepare the data based on tracker type
        if tracker_type == 'weight':
            weight_in_kg = form.weight.data
            new_tracker = tracker_model(pet_id=pet_id, weight_in_kg=weight_in_kg, date=date, notes=notes)
        elif tracker_type == 'vaccine':
            vaccine_name = form.vaccine_name.data
            next_dosis = form.next_dosis.data
            administered_by = form.administered_by.data
            new_tracker = tracker_model(
                pet_id=pet_id, vaccine_name=vaccine_name, date=date,
                next_dosis=next_dosis, administered_by=administered_by, notes=notes
            )
        elif tracker_type == 'internal_deworming':
            product_name = form.product_name.data
            next_dosis = form.next_dosis.data
            new_tracker = tracker_model(
                pet_id=pet_id, product_name=product_name, date=date, next_dosis=next_dosis, notes=notes
            )
        elif tracker_type == 'external_deworming':
            product_name = form.product_name.data
            next_dosis = form.next_dosis.data
            new_tracker = tracker_model(
                pet_id=pet_id, product_name=product_name, date=date, next_dosis=next_dosis, notes=notes
            )
        elif tracker_type == 'medication':
            product_name = form.product_name.data
            date = form.date.data
            next_dosis = form.next_dosis.data
            new_tracker = tracker_model(
                pet_id=pet_id, product_name=product_name, date=date, next_dosis=next_dosis, notes=notes
            )
        else:
            return error_message("An error has occurred", 400)

        # Add new tracker to the database
        db.session.add(new_tracker)
        db.session.commit()

        flash("Data successfully added", "info")

        # Redirect to the previous page
        return redirect(url_for('trackers.trackers_home', pet_id=pet_id))

    return render_template('tracker_add.html', form=form, tracker_type=tracker_type, pet_id=pet_id)


@trackers_bp.route('/<int:pet_id>/weight_graph')
@login_required
def weight_graph(pet_id):
    weight_entries = WeightTracker.query.filter_by(pet_id=pet_id).order_by(WeightTracker.date).all()
    pet = Pet.query.get_or_404(pet_id)

    dates = [entry.date for entry in weight_entries]
    weights = [entry.weight_in_kg for entry in weight_entries]

    fig, ax = plt.subplots()
    ax.plot(dates, weights, marker='o', color='b')
    ax.set(xlabel='Date', ylabel='Weight (kg)', title="Pet's Weight Over Time")
    ax.grid()

    # Save the plot to a BytesIO object to display it on the page
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    img_data = base64.b64encode(img.getvalue()).decode('utf-8')

    return render_template('weight_graph.html', img_data=img_data, pet=pet, pet_id=pet.id)

@trackers_bp.route('/<int:pet_id>/vaccinations')
def vaccinations(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('vaccination_tracker.html', pet_id=pet.id)

@trackers_bp.route('/<int:pet_id>/internal_deworming')
def internal_deworming(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('internal_deworming_tracker.html', pet=pet)

@trackers_bp.route('/<int:pet_id>/external_deworming')
def external_deworming(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('external_deworming_tracker.html', pet=pet)

@trackers_bp.route('/<int:pet_id>/medications')
def medications(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return render_template('medication_tracker.html', pet=pet)