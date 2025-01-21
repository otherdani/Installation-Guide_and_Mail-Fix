import os
from flask import Blueprint, render_template, request, redirect, flash, current_app, session, jsonify
from werkzeug.utils import secure_filename

from models import Pet, Breed, Species
from forms import PetForm
from helpers import error_message, login_required, allowed_photo_file

pet_bp = Blueprint('pet', __name__)

@pet_bp.route("/new_pet", methods=["GET", "POST"])
@login_required
def add_new_pet():
    """Add new pet to database"""
    form = PetForm()
    db = current_app.extensions['sqlalchemy']

    # Populate species and breed choices dynamically
    form.species.choices = [(species.id, species.name) for species in Species.query.all()]
    if form.species.data:
        form.breed.choices = [(breed.id, breed.name) for breed in Breed.query.filter_by(species_id=form.species.data).all()]
    
    # User reached route via POST
    if request.method == 'POST':
        if form.validate_on_submit():
            # Extract form data
            pet_name = form.name.data
            birth_date = form.birth_date.data
            adoption_date = form.adoption_date.data
            sex = form.sex.data
            species_id = form.species.data
            breed_id = form.breed.data
            sterilized = form.sterilized.data
            microchip_number = form.microchip_number.data
            insurance_company = form.insurance_company.data
            insurance_number = form.insurance_number.data

            # Handling the uploaded pet profile photo
            if form.pet_profile_photo.data and allowed_photo_file(form.pet_profile_photo.data.filename):
                photo = form.pet_profile_photo.data
                filename = secure_filename(photo.filename)
                pet_profile_photo = filename
                photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                
            else:
                pet_profile_photo = None

            # Save pet data to the database
            new_pet = Pet(
                user_id=session["user_id"],
                pet_profile_photo=pet_profile_photo,
                name=pet_name,
                birth_date=birth_date,
                adoption_date=adoption_date,
                sex=sex,
                species_id=species_id,
                breed_id=breed_id,
                sterilized=sterilized,
                microchip_number=microchip_number,
                insurance_company=insurance_company,
                insurance_number=insurance_number
            )
            db.session.add(new_pet)
            db.session.commit()

            flash('Pet registered successfully!', 'success')
            return redirect("/")

        else:
            return error_message("An error occurred. Please try again.", form.errors)
        
    # User reached route via GET
    return render_template('new_pet.html', form=form)

@pet_bp.route('/delete_pet/<int:pet_id>', methods=['GET'])
@login_required
def delete_pet(pet_id):
    """Delete a pet from db"""
    pet = Pet.query.get_or_404(pet_id)
    db = current_app.extensions['sqlalchemy']
    
    # Delete pet photo
    if pet.pet_profile_photo:
        old_photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pet.pet_profile_photo)
        if os.path.exists(old_photo_path):
            try:
                os.remove(old_photo_path)
                current_app.logger.info(f"Deleted photo: {old_photo_path}")
            except Exception as e:
                current_app.logger.error(f"Error deleting pet photo: {e}")
    
    try:
        db.session.delete(pet)
        db.session.commit()
        flash('Pet deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting pet: {str(e)}")
        flash(f'Error deleting pet: {str(e)}', 'danger')
    
    return redirect('/')


@pet_bp.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    """Edit pet info"""
    pet = Pet.query.get_or_404(pet_id)
    form = PetForm(obj=pet)
    db = current_app.extensions['sqlalchemy']

    # Populate species and breed choices dynamically
    form.species.choices = [(species.id, species.name) for species in Species.query.all()]
    if form.species.data:
        form.breed.choices = [(breed.id, breed.name) for breed in Breed.query.filter_by(species_id=form.species.data).all()]
    
    if form.validate_on_submit():
        try:
            pet.name = form.name.data
            pet.birth_date = form.birth_date.data
            pet.adoption_date = form.adoption_date.data
            pet.sex = form.sex.data
            pet.species_id = form.species.data
            pet.breed_id = form.breed.data
            pet.sterilized = form.sterilized.data
            pet.microchip_number = form.microchip_number.data
            pet.insurance_company = form.insurance_company.data
            pet.insurance_number = form.insurance_number.data
            if form.pet_profile_photo.data:
                # Delete old photo if it exists
                if pet.pet_profile_photo and allowed_photo_file(form.pet_profile_photo.data.filename):
                    old_photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pet.pet_profile_photo)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                
                # Save new photo
                photo = form.pet_profile_photo.data
                filename = secure_filename(photo.filename)
                pet.pet_profile_photo = filename
                photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)

            db.session.commit()
            flash('Pet information updated successfully!', 'success')
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating pet: {str(e)}")
            flash(f'Error updating pet: {str(e)}', 'danger')

    # User reached route via GET
    if request.method == 'GET':
        form.name.data = pet.name
        form.birth_date.data = pet.birth_date
        form.adoption_date.data = pet.adoption_date
        form.sex.data = pet.sex
        form.species.data = pet.species_id
        form.breed.data = pet.breed_id
        form.sterilized.data = pet.sterilized
        form.microchip_number.data = pet.microchip_number
        form.insurance_company.data = pet.insurance_company
        form.insurance_number.data = pet.insurance_number
    return render_template('edit_pet.html', form=form, pet=pet)

@pet_bp.route('/get_breeds/<int:species_id>', methods=['GET'])
@login_required
def get_breeds(species_id):
    """Show breed list"""
    breeds = Breed.query.filter_by(species_id=species_id).all()
    breed_data = [{"id": breed.id, "name": breed.name} for breed in breeds]
    return jsonify(breed_data)
