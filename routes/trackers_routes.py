from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, current_app, flash, request
import matplotlib
import calendar

from helpers import login_required, inject_pets, error_message, create_weight_graph
from models import Pet, WeightTracker, VaccineTracker, InternalDewormingTracker, ExternalDewormingTracker, MedicationTracker
from forms import WeightForm, VaccineForm, InternalDewormingForm, ExternalDewormingForm, MedicationForm

# Use backend without graphic interface to avoid sockets conflict
matplotlib.use('Agg')

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


@trackers_bp.route('/<int:pet_id>/weight_graph', methods=['GET'])
@login_required
def weight_graph(pet_id):
    """Display a graph of pet weight for the current or specified month."""
    weight_entries = WeightTracker.query.filter_by(pet_id=pet_id).order_by(WeightTracker.date).all()
    pet = Pet.query.get_or_404(pet_id)

    # Get current date and parse month/year from request args
    month = request.args.get('month', default=datetime.now().month, type=int)
    year = request.args.get('year', default=datetime.now().year, type=int)

    # Generate all days of the specified month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])
    all_days = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]

    # Map user-provided data to corresponding days
    weight_data = {entry.date: entry.weight_in_kg for entry in weight_entries if entry.date.month == month and entry.date.year == year}
    monthly_weights = [weight_data.get(day.date(), None) for day in all_days]

    # Check if there is any data for the month
    if not any(monthly_weights):
        return render_template(
            'weight_graph.html',
            pet=pet,
            year=year,
            month=month,
            month_name=first_day.strftime('%B'),
            monthly_img_data=None,
            current_month=datetime.now().month,
            current_year=datetime.now().year,
        )

    # Monthly graph
    monthly_img_data = create_weight_graph(
        dates=all_days,
        weights=monthly_weights,
        title=f"Pet's Weight for {first_day.strftime('%B %Y')}",
        xlabel='Day',
        ylabel='Weight (kg)',
        color='g',
        show_days_only=True
    )

    return render_template(
        'weight_graph.html',
        pet=pet,
        year=year,
        month=month,
        month_name=first_day.strftime('%B'),
        monthly_img_data=monthly_img_data,
        current_month=datetime.now().month,
        current_year=datetime.now().year,
    )


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