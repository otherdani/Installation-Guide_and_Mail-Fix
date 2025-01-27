from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for

from helpers import login_required, inject_pets
from models import Pet, Log
from forms import EntryForm

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs/<int:pet_id>', methods=['GET'])
@login_required
@inject_pets
def pet_logs(pet_id):
    """Display logs"""
    pet = Pet.query.get_or_404(pet_id)
    logs = Log.query.filter_by(pet_id=pet_id).order_by(Log.date_uploaded.desc()).all()

    return render_template('logs.html', pet=pet, logs=logs)

@logs_bp.route('/new_entry/<int:pet_id>', methods=['GET', 'POST'])
@login_required
@inject_pets
def new_entry(pet_id):
    """Add new entry"""
    form = EntryForm()
    pet = Pet.query.get_or_404(pet_id)
    db = current_app.extensions['sqlalchemy']
    # User reaches via post
    if request.method == 'POST':
        # Extract form data
        title = form.title.data
        content = form.content.data
        date_uploaded = form.date_uploaded.data

        # Save entry to database
        new_log = Log(
            pet_id=pet_id,
            title=title,
            date_uploaded=date_uploaded,
            content=content
        )
        db.session.add(new_log)
        db.session.commit()

        flash('New Entry added!', 'success')
        return redirect(url_for('logs.pet_logs', pet_id=pet.id))

    return render_template('new_entry.html', pet=pet, form=form)

@logs_bp.route("/delete_entry/<int:entry_id>", methods=['GET'])
@login_required
def delete_entry(entry_id):
    """Delete photo of a pet"""
    entry = Log.query.get_or_404(entry_id)
    db = current_app.extensions['sqlalchemy']
    
    # Delete from database
    db.session.delete(entry)
    db.session.commit()

    flash('Entry deleted successfully.', 'success')
    return redirect(url_for('logs.pet_logs', pet_id=entry.pet_id))

@logs_bp.route('/read_entry/<int:entry_id>', methods=['GET'])
@login_required
@inject_pets
def read_entry(entry_id):
    """Read an entry"""
    entry = Log.query.get_or_404(entry_id)
    return render_template('entry.html', entry=entry)

@logs_bp.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
@inject_pets
def edit_entry(entry_id):
    """Edit an entry"""
    entry = Log.query.get_or_404(entry_id)
    form = EntryForm(obj=entry)
    db = current_app.extensions['sqlalchemy']
    
    # User reached route via POST
    if form.validate_on_submit():
        try:
            entry.title = form.title.data
            entry.content = form.content.data
            entry.date_uploaded = form.date_uploaded.data

            db.session.commit()
            flash('Entry updated!', 'success')
            return redirect(url_for('logs.pet_logs', pet_id=entry.pet_id))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating entry: {str(e)}")
            flash(f'Error updating entry: {str(e)}', 'danger')

    # User reached route via GET
    if request.method == 'GET':
        form.title.data = entry.title
        form.content.data = entry.content
        form.date_uploaded.data = entry.date_uploaded
    return render_template('edit_entry.html', form=form, entry=entry)
