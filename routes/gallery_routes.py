import os
from flask import Blueprint, render_template, request, flash, redirect, current_app, url_for
from werkzeug.utils import secure_filename

from models import Pet, Photo
from forms import PhotoForm
from helpers import allowed_photo_file, inject_pets, login_required

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route("/gallery/<int:pet_id>", methods=['GET'])
@login_required
@inject_pets
def gallery(pet_id):
    """Display pet gallery"""
    pet = Pet.query.get_or_404(pet_id)
    photos = Photo.query.filter_by(pet_id=pet_id).order_by(Photo.date_uploaded.desc()).all()
    photo_data = [photo.to_dict() for photo in photos]
    return render_template('gallery.html', pet=pet,  photos=photo_data)

@gallery_bp.route("/upload_photo/<int:pet_id>", methods=['GET', 'POST'])
@login_required
def upload_photo(pet_id):
    """Add a new photo of a pet"""
    form=PhotoForm()
    pet = Pet.query.get_or_404(pet_id)
    db = current_app.extensions['sqlalchemy']
    # User reaches via post
    if request.method == 'POST':
        if form.validate_on_submit():
            # Extract form data
            title = form.title.data
            date_uploaded = form.date_uploaded.data

            # Handling the uploaded pet photo
            if form.image.data and allowed_photo_file(form.image.data.filename):
                image = form.image.data
                filename = secure_filename(image.filename)
                image_url = filename
                photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(photo_path)
                
            else:
                image_url = None

            # Save pet data to the database
            new_photo = Photo(
                pet_id=pet_id,
                image_url=image_url,
                title=title,
                date_uploaded=date_uploaded
            )
            db.session.add(new_photo)
            db.session.commit()

            flash('Pet photo added!', 'success')
            return redirect(url_for('gallery.gallery', pet_id=pet.id))

    #User reaches via get
    return render_template('upload_photo.html', pet=pet, form=form)

@gallery_bp.route("/delete_photo/<int:photo_id>", methods=['GET'])
@login_required
def delete_photo(photo_id):
    """Delete photo of a pet"""
    photo = Photo.query.get_or_404(photo_id)
    db = current_app.extensions['sqlalchemy']

    if photo.image_url:
        try:
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.image_url)
            os.remove(photo_path)
        except FileNotFoundError:
            flash('Photo file not found.', 'danger')
            return redirect(url_for('gallery.gallery', pet_id=photo.pet_id))
    
    # Delete from database
    db.session.delete(photo)
    db.session.commit()

    flash('Photo deleted successfully.', 'success')
    return redirect(url_for('gallery.gallery', pet_id=photo.pet_id))
