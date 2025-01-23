from flask import Blueprint, render_template, request

from models import Pet, Photo
from forms import PhotoForm
from helpers import login_required

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route("/gallery/<int:pet_id>", methods=['GET'])
@login_required
def gallery(pet_id):
    """Display pet gallery"""
    pet = Pet.query.get_or_404(pet_id)
    photos = Photo.query.filter_by(pet_id=pet_id).order_by(Photo.date_uploaded.desc()).all()
    print(photos)
    photo_data = [photo.to_dict() for photo in photos]
    return render_template('gallery.html', pet=pet,  photos=photo_data)

@gallery_bp.route("/upload_photo/<int:pet_id>", methods=['GET', 'POST'])
@login_required
def upload_photo(pet_id):
    """Add a new photo of a pet"""
    form=PhotoForm()
    pet = Pet.query.get_or_404(pet_id)
    # User reaches via post
    if request.method == 'POST':
        if form.validate_on_submit():
            return("Photo uploaded")

    #User reaches via get
    return render_template('upload_photo.html', pet=pet, form=form)
